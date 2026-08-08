from fastapi import FastAPI, HTTPException, Request, Depends
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

from utils.colour_utils import hsv_to_rgb_array

app = FastAPI()


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



class Backend:
    """A single object that holds all game state - replaces appController"""
    def __init__(self):
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS)
        self.story_engine = StoryEngine(self.world)
        self.editor = WorldEditor(self.world)

        if config.MAP_NAME:
            try:
                self.load_map(config.MAP_NAME)
            except Exception:
                print("invalid map file name - generating procedural map")
                self.generate_map()
        else:
            self.generate_map()
        
    def generate_map(self):
        with open(SAVED_MAPS / "default_config.yaml") as f:
            biome_config = yaml.safe_load(f)
        
        self.world.load_data(biome_config)

        self.story_engine.clear_setup()

        self.reset_player()

    
    def load_map(self, name):
        path = SAVED_MAPS / name
        with open(path / "story_setup.yaml") as f:
            self.story_engine.setup(yaml.safe_load(f))
        with open(path / "biome_config.yaml") as f:
            biome_config = yaml.safe_load(f)
        world_data = np.load(path / "map_data.npz", allow_pickle=True)
        rows, cols = world_data["biome"].shape
        config.WORLD_ROWS, config.WORLD_COLS = rows, cols
        self.world.rows, self.world.cols = rows, cols
        self.world.load_data(biome_config, world_data)
        self.reset_player()

    def save_map(self, name):
        path = SAVED_MAPS / name
        path.mkdir(parents=True, exist_ok=True)
        map_data, region_data, biome_config = self.world.get_data()
        np.savez(
            path / "map_data",
            **map_data,
            region_map=np.array(region_data["map"], dtype=object),
            region_list=np.array(region_data["list"], dtype=object),
        )
        with open(path / "biome_config.yaml", "w") as f:
            yaml.dump(biome_config, f, sort_keys=False)
        with open(path / "story_setup.yaml", "w") as f:
            yaml.dump(self.story_engine.get_setup(), f, sort_keys=False)

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
    user = token["userinfo"]          # already-verified ID token claims
    request.session["user"] = {
        "sub": user["sub"],           # Google's stable user id — use this as your key
        "email": user["email"],
        "name": user.get("name"),
    }
    return RedirectResponse(FRONTEND_URL)

@app.get("/api/auth/me")
def me(request: Request):
    return request.session.get("user")


@app.post("/api/auth/logout")
def logout(request: Request):
    request.session.clear()
    return {"ok": True}

def get_user(request: Request):
    """The logged-in user, or None."""
    return request.session.get("user")


def require_user(request: Request):
    user = request.session.get("user")
    if not user:
        raise HTTPException(status_code=401, detail="Login required")
    return user

def session_key(request: Request) -> str:
    user = request.session.get("user")
    if user:
        return f"google:{user['sub']}"
    if "guest_id" not in request.session:
        request.session["guest_id"] = str(uuid.uuid4())
    return f"guest:{request.session['guest_id']}"

def get_backend(request: Request) -> Backend:
    key = session_key(request)
    if key not in backends:
        backends[key] = Backend()
    return backends[key]

active_streams: dict[str, str] = {}

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
    
@app.get("/api/world/region-lookup")
def get_region_lookup(b: Backend = Depends(get_backend)):
    return b.world.get_region_lookup()

@app.get("/api/world/region-map")
def get_region_map(b: Backend = Depends(get_backend)):
    region_map_flat = b.world.get_region_map_flattened()  # shape (rows, cols, MAX_REGIONS_PER_CELL)
    return Response(region_map_flat.tobytes(), media_type="application/octet-stream")

@app.get('/api/token-usage')
def get_token_usage(b: Backend = Depends(get_backend)):
    return {
        "output_tokens": b.story_engine.state.completion_tokens,
        "input_tokens": b.story_engine.state.prompt_tokens
    }

