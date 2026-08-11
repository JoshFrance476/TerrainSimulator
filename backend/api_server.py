import traceback

from database.db import pool


from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse, Response
from sse_starlette.sse import EventSourceResponse
from authlib.integrations.starlette_client import OAuth

from pathlib import Path
import yaml
import numpy as np
from PIL import Image
import io
from pydantic import BaseModel
import uuid

from world.world import World
from world.map_entity import MapEntity
from storytelling.story_engine import StoryEngine
from editor.world_editor import WorldEditor
import config as config

from database import users, worlds

from utils.colour_utils import hsv_to_rgb_array


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open()
    yield
    pool.close()    


app = FastAPI(lifespan=lifespan)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],   # your Vite dev server, not "*"
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=config.SESSION_SECRET,   # load from env, keep it stable across restarts
    same_site="lax",
    https_only=False,                   # True in production
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=config.GOOGLE_CLIENT_ID,
    client_secret=config.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


FRONTEND_URL = "http://localhost:5173"

SAVED_MAPS = Path("data/saved_maps")

# ---------------------------------------------------------------- models
class CellBody(BaseModel):
    x: int
    y: int


class ActionBody(BaseModel):
    action: str

class MoveDestinationBody(BaseModel):
    x: int
    y: int

class PromptBody(BaseModel):
    text: str
    temperature: float | None
    max_tokens: int = None
    reasoning_effort: str = None

class SaveWorldBody(BaseModel):
    name: str
    description: str = ""

class StartSessionBody(BaseModel):
    world_id: int | None = None


class Backend:
    """A single object that holds all game state - replaces appController"""
    def __init__(self, world_id: int | None = None):
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS)
        self.story_engine = StoryEngine(self.world)
        self.editor = WorldEditor(self.world)

        if world_id is None:
            self.generate_map()
        else:
            self.load_map_from_database(world_id)
        
    def generate_map(self):
        with open(SAVED_MAPS / "default_config.yaml") as f:
            biome_config = yaml.safe_load(f)
        
        self.world.load_world(biome_config, None, None)

        self.story_engine.clear_setup()

        self.reset_player()

    def load_map_from_database(self, world_id):
        row = worlds.get_world(world_id)
        if row is None:
            raise ValueError(f"World with ID {world_id} not found in database.")

        self.story_engine.setup(row["story_setup"])

        with np.load(io.BytesIO(row["map_data"])) as npz:
            world_data = {key: npz[key] for key in npz.files}

        rows, cols = world_data["biome"].shape
        config.WORLD_ROWS, config.WORLD_COLS = rows, cols
        self.world.rows, self.world.cols = rows, cols
        self.world.load_world(row["biome_config"], world_data, row["region_list"])
        self.reset_player()
                

    def save_current_map(self, name, description, user_id):
        worlds.upsert_save(
            name=name, 
            description=description,
            owner_id=user_id,
            map_data=self.convert_map_data_to_npz(),
            map_png=self.get_map_thumbnail(),
            biome_config=self.world.get_biome_config(),
            story_setup=self.story_engine.get_setup(),
            region_list=self.world.get_region_list()
        )
        
    def convert_map_data_to_npz(self):
        map_data = self.world.get_all_map_data()
        buf = io.BytesIO()
        np.savez(
            buf,
            **{k: v for k, v in map_data.items() if k != "region_list"},
        )
        return buf.getvalue()

    def get_map_thumbnail(self):
        rgb = np.asarray(hsv_to_rgb_array(self.world.get_map_data("colour")), dtype=np.uint8)
        buf = io.BytesIO()
        Image.fromarray(rgb).save(buf, format="PNG")
        return buf.getvalue()


    def reset_player(self):
        self.player = MapEntity(
            location=self.world.get_starting_location(),
            boundary=(config.WORLD_ROWS, config.WORLD_COLS),
        )

    # -- serialisation helpers -------------------------------------------
    def get_current_scene_json(self):
        scene = self.story_engine.get_current_scene()
        if not scene:
            return None
        return scene.to_dict()
    

    def get_world_json(self):
        return { 
            "rows": self.world.rows,
            "cols": self.world.cols,
            "setup": self.story_engine.get_setup(),
            "max_regions_per_cell": self.world.region_manager.MAX_REGIONS_PER_CELL,
            "no_region_id": self.world.region_manager.NO_REGION,
        }

    def get_story_json(self):
        return {
            "character_history": self.story_engine.state.character_history,
            "quests_list": self.story_engine.state.quest_list,
        }


backends: dict[str, Backend] = {}

@app.get("/api/auth/login")
async def login(request: Request):
    redirect_uri = request.url_for("auth_callback")
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/callback")
async def auth_callback(request: Request):
    token = await oauth.google.authorize_access_token(request)
    claims = token["userinfo"]

    user = users.get_user_by_provider("google", claims["sub"])
    if user is None:
        user = users.create_user("google", claims["sub"], claims["email"], claims.get("name"))

    guest_backend = backends.pop(session_key(request), None)

    request.session.clear()
    request.session["user_id"] = user["id"]

    if guest_backend:
        backends[session_key(request)] = guest_backend
    
    return RedirectResponse(FRONTEND_URL)

@app.get("/api/auth/me")
def me(request: Request):
    session_key(request)    
    user_id = request.session.get("user_id")
    return users.get_user(user_id) if user_id else None


@app.post("/api/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}


def require_user(request: Request):
    user_id = request.session.get("user_id")
    user = users.get_user(user_id) if user_id else None
    if user is None or user["provider"] is None:
        raise HTTPException(status_code=401, detail="Login required")
    return user

def session_key(request: Request) -> str:
    user_id = request.session.get("user_id")
    if user_id is not None:
        return f"user:{user_id}"
    if "guest_id" not in request.session:
        request.session["guest_id"] = str(uuid.uuid4())
    return f"guest:{request.session['guest_id']}"

def get_backend(request: Request) -> Backend:
    backend = backends.get(session_key(request))
    if backend is None:
        raise HTTPException(status_code=409, detail="No active session")
    return backend


active_streams: dict[str, str] = {}

@app.post("/api/session")
def create_session(body: StartSessionBody, request: Request):
    try:
        backends[session_key(request)] = Backend(body.world_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ok":True}
# ---------------------------------------------------------------- story

@app.get("/api/story")
def get_story(b: Backend = Depends(get_backend)):
    return b.get_story_json()

@app.get("/api/scene") 
def get_scene(b: Backend = Depends(get_backend)):
    return b.get_current_scene_json()


@app.post("/api/scene/prompt")
async def prompt_scene(body: CellBody, request: Request, user=Depends(require_user), b: Backend = Depends(get_backend)):
    stream_id = str(uuid.uuid4())
 
    active_streams[stream_id] = {  
        "key": session_key(request),
        "cell": (body.y, body.x),
    } 
    return {"stream_id": stream_id} 


@app.get("/api/stream")
async def stream_response(id: str, request: Request, b: Backend = Depends(get_backend)) -> Response:
    data = active_streams.get(id)

    if not data or data["key"] != session_key(request):
        raise HTTPException(status_code=404, detail="Stream ID not found")
    
    if not data.get("cell") and not b.story_engine.get_current_scene():
        raise HTTPException(status_code=404, detail="No cell provided and no existing scene")

    async def generate():
        async for event in b.story_engine.generate_scene_interaction(data.get("cell")):
            yield event
 
    return EventSourceResponse(generate())

@app.post("/api/scene/action") 
async def scene_action(body: ActionBody, b: Backend = Depends(get_backend)):
    await b.story_engine.choose_action(body.action, tuple(b.player.get_location()))
    scene = b.story_engine.get_current_scene()
    return {"ended": scene.ended if scene else True}


@app.put("/api/scene/templates/{name}")
async def set_prompt_template(name: str, body: PromptBody, b: Backend = Depends(get_backend)):
    try:
        b.story_engine.llm.prompt_manager.set(name, body.text, body.temperature, body.max_tokens, body.reasoning_effort)
    except KeyError:
        raise HTTPException(status_code=404, detail="Template not found")


@app.get("/api/scene/templates/{name}")
def get_prompt_template(name: str, b: Backend = Depends(get_backend)): 
    return b.story_engine.llm.prompt_manager.get(name).to_dict()

# ---------------------------------------------------------------- player

@app.post('/api/player/move')
async def move_player_to(body: MoveDestinationBody, b: Backend = Depends(get_backend)):
    new_location = (body.y, body.x)
    b.player.set_location(new_location)
    return {"player_location": list(b.player.get_location())}

@app.get('/api/player')
def get_player_location(b: Backend = Depends(get_backend)):
    return {"player_location": list(b.player.get_location())}

# ---------------------------------------------------------------- world
@app.get("/api/world")
def get_world(b: Backend = Depends(get_backend)):
    return b.get_world_json()

@app.post("/api/world/save")
def save_world(body: SaveWorldBody, user=Depends(require_user), b: Backend = Depends(get_backend)):
    b.save_current_map(body.name, body.description, user["id"])
    return {"ok": True}

@app.get("/api/world/rgb")
def get_world_rgb(b: Backend = Depends(get_backend)):
    rgb = hsv_to_rgb_array(b.world.get_map_data("colour"))          # shape (rows, cols, 3)
    rgb = np.asarray(rgb, dtype=np.uint8)
    alpha = np.full((*rgb.shape[:2], 1), 255, dtype=np.uint8)       # fully opaque
    rgba = np.concatenate([rgb, alpha], axis=2)                      # shape (rows, cols, 4)
    return Response(rgba.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/biome-map")
def get_biome_map(b: Backend = Depends(get_backend)):
    biome_map = b.world.get_biome_map().astype(np.uint8)
    return Response(biome_map.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/biome-lookup")
def get_biome_lookup(b: Backend = Depends(get_backend)):
    return b.world.get_biome_lookup()
    
@app.get("/api/world/region-map")
def get_region_map(b: Backend = Depends(get_backend)):
    return Response(b.world.get_region_map().tobytes(), media_type="application/octet-stream")

@app.get("/api/world/region-lookup")
def get_region_lookup(b: Backend = Depends(get_backend)):
    return b.world.get_region_lookup()

@app.get('/api/token-usage')
def get_token_usage(b: Backend = Depends(get_backend)):
    return {
        "output_tokens": b.story_engine.state.completion_tokens,
        "input_tokens": b.story_engine.state.prompt_tokens
    }

# ---------------------------------------------------------------- worlds

@app.get("/api/worlds")
def list_worlds():
    return worlds.list_worlds()

@app.get("/api/worlds/{world_id}/thumbnail")
def get_world_thumbnail(world_id: int):
    png = worlds.get_world_png(world_id)
    if png is None:
        raise HTTPException(status_code=404, detail="World not found")
    return Response(png, media_type="image/png")