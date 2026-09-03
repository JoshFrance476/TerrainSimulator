import base64

import os
from dotenv import load_dotenv

load_dotenv()

from database.db import pool


from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from fastapi.responses import RedirectResponse, Response
from sse_starlette.sse import EventSourceResponse
from authlib.integrations.starlette_client import OAuth

from pathlib import Path
import numpy as np
from PIL import Image
import io
import uuid
import json

from models import (
    Location,
    SaveWorldPayload,
    StartSessionBody,
    SetupStoryBody,
    CellBody,
    ActionBody,
    PromptBody,
    MoveDestinationBody,
    SaveWorldBody,
    WorldData,
    WorldPayload,
    to_payload,
    to_data,
    StorySetup,
    StorylinesBody,
    CharacterSetupBody
)

from world import World
from story_generation.story_engine import StoryEngine

from database import users, worlds


SESSION_SECRET = os.environ["SESSION_SECRET"]
GOOGLE_CLIENT_ID = os.environ["GOOGLE_CLIENT_ID"]
GOOGLE_CLIENT_SECRET = os.environ["GOOGLE_CLIENT_SECRET"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    pool.open(wait=True, timeout=10)
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
    secret_key=SESSION_SECRET,   # load from env, keep it stable across restarts
    same_site="lax",
    https_only=False,                   # True in production
)

oauth = OAuth()
oauth.register(
    name="google",
    client_id=GOOGLE_CLIENT_ID,
    client_secret=GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email profile"},
)


FRONTEND_URL = "http://localhost:5173"

SAVED_MAPS = Path("data/saved_maps")

# ---------------------------------------------------------------- models


class Session:
    def __init__(self, world_id: int):
        world_data = load_world(world_id)
        self.world = World(world_data)
        self.story_engine = StoryEngine(self.world)
        

    # -- serialisation helpers -------------------------------------------
    def get_current_scene_json(self):
        scene = self.story_engine.get_current_scene()
        if not scene:
            return None
        return scene.to_dict()
    

    def get_world_json(self):
        return { 
            "width": self.world.width,
            "height": self.world.height,
            "setup": self.story_engine.get_setup(),
            "max_regions_per_cell": self.world.max_regions_per_cell,
            "no_region_id": self.world.no_region_sentinel,
        }

    def get_story_json(self):
        return {
            "character_history": self.story_engine.state.character_history,
            "quests_list": self.story_engine.state.quest_list,
        }

sessions: dict[str, Session] = {}
active_streams: dict[str, str] = {}

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

    guest_session = sessions.pop(session_key(request), None)

    request.session.clear()
    request.session["user_id"] = user["id"]

    if guest_session:
        sessions[session_key(request)] = guest_session
    
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

def get_session(request: Request) -> Session:
    session = sessions.get(session_key(request))
    if session is None:
        raise HTTPException(status_code=409, detail="No active session")
    return session


@app.post("/api/session")
def create_session(body: StartSessionBody, request: Request):
    try:
        sessions[session_key(request)] = Session(body.world_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    return {"ok":True}
 
@app.post("/api/session/story-setup")
def setup_session_story(body: SetupStoryBody, s: Session = Depends(get_session)):

    s.story_engine.setup(StorySetup(
        world_description=body.world_description,
        character_description=body.character_description,
        story_focus_description=body.story_focus_description
    ))

# ---------------------------------------------------------------- story

@app.get("/api/story")
def get_story(s: Session = Depends(get_session)):
    return s.get_story_json()

@app.get("/api/scene") 
def get_scene(s: Session = Depends(get_session)):
    return s.get_current_scene_json()

@app.post("/api/scene/generate-guide")
async def prompt_scene_guide(body: CellBody, user=Depends(require_user), s: Session = Depends(get_session)):
    return EventSourceResponse(sse_events(s.story_engine.generate_scene_guide(Location(body.x, body.y))))

@app.post("/api/scene/generate-interaction")
async def prompt_interaction(user=Depends(require_user), s: Session = Depends(get_session)):
    return EventSourceResponse(sse_events(s.story_engine.generate_interaction()))

@app.post("/api/setup/generate-storylines")
async def generate_storylines(body: SetupStoryBody, user=Depends(require_user), s: Session = Depends(get_session)):
    return EventSourceResponse(sse_events(s.story_engine.generate_storylines(body)))

@app.post("/api/scene/generate-summary")
async def prompt_scene_summary(user=Depends(require_user), s: Session = Depends(get_session)):
    return await s.story_engine.generate_scene_summary()

async def sse_events(source):
    """Domain events -> sse_starlette's wire shape."""
    async for event in source:
        payload = event["payload"]
        yield {
            "event": event["event"],
            "data": payload if isinstance(payload, str) else json.dumps(payload),
        }


@app.post("/api/scene/action") 
async def scene_action(body: ActionBody, s: Session = Depends(get_session)):
    await s.story_engine.choose_action(body.action)
    scene = s.story_engine.get_current_scene()
    return {"ended": scene.ended if scene else True}
    

@app.put("/api/scene/templates/{name}")
async def set_prompt_template(name: str, body: PromptBody, s: Session = Depends(get_session)):
    try:
        s.story_engine.llm.prompt_manager.set(name, body.text, body.temperature, body.max_tokens, body.reasoning_effort)
    except KeyError:
        raise HTTPException(status_code=404, detail="Template not found")


@app.get("/api/scene/templates/{name}")
def get_prompt_template(name: str, s: Session = Depends(get_session)): 
    return s.story_engine.llm.prompt_manager.get(name)

# ---------------------------------------------------------------- player

@app.post('/api/player/move')
async def move_player_to(body: MoveDestinationBody, s: Session = Depends(get_session)):
    new_location = Location(body.x, body.y)
    s.story_engine.set_player_location(new_location)

@app.get('/api/player')
def get_player_location(s: Session = Depends(get_session)):
    return s.story_engine.get_player_location()

# ---------------------------------------------------------------- world
@app.get("/api/world")
def get_world(s: Session = Depends(get_session)):
    return s.get_world_json()


@app.get("/api/world/elevation-map")
def get_elevation_map(s: Session = Depends(get_session)):
    return Response(s.world.elevation.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/biome-map")
def get_biome_map(s: Session = Depends(get_session)):
    return Response(s.world.biome.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/biome-lookup")
def get_biome_lookup(s: Session = Depends(get_session)):
    return s.world.biome_lookup
    
@app.get("/api/world/region-map")
def get_region_map(s: Session = Depends(get_session)):
    return Response(s.world.region.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/region-lookup")
def get_region_lookup(s: Session = Depends(get_session)):
    return s.world.region_lookup

@app.get("/api/world/detail-map")
def get_detail_map(s: Session = Depends(get_session)):
    return Response(s.world.detail.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/detail-lookup")
def get_detail_lookup(s: Session = Depends(get_session)):
    return s.world.detail_lookup

@app.get("/api/world/component-map")
def get_component_map(s: Session = Depends(get_session)):
    return Response(s.world.component.tobytes(), media_type="application/octet-stream")

@app.get("/api/world/component-lookup")
def get_component_lookup(s: Session = Depends(get_session)):
    return s.world.component_lookup

@app.get('/api/token-usage')
def get_token_usage(s: Session = Depends(get_session)):
    return s.story_engine.get_token_usage()

# ---------------------------------------------------------------- setup

@app.post("/api/setup/generate-storylines")
async def generate_storylines(body: SetupStoryBody, s: Session = Depends(get_session), user=Depends(require_user)):
    return await s.story_engine.generate_storylines(body)

@app.post("/api/setup/generate-hidden-context")
async def generate_hidden_context(body: StorylinesBody, s: Session = Depends(get_session), user=Depends(require_user)):
    return await s.story_engine.generate_hidden_context(body)

@app.post("/api/setup/generate-character-setup")
async def generate_character_setup(body: CharacterSetupBody, s: Session = Depends(get_session), user=Depends(require_user)):
    return await s.story_engine.generate_character_setup(body.character_description, body.world_description, body.focus_description)

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


# ---------------------------------------------------------------- editor

def load_world(world_id: int) -> WorldData:
    row = worlds.get_world(world_id)
    if row is None:
        raise LookupError(f"World with ID {world_id} not found in database.")
    return WorldData(
        name=row["name"],
        description=row["description"],
        width=row["width"],
        height=row["height"],
        biome=row["biome"],
        elevation=row["elevation"],
        region=row["region"],
        biome_lookup=row["biome_lookup"],
        story_setup=row["story_setup"],
        region_lookup=row["region_lookup"],
        detail_lookup=row["detail_lookup"],
        component_lookup=row["component_lookup"],
        detail=row["detail"],
        component=row["component"]
    )

@app.get("/api/load-world/{world_id}")
def load_world_endpoint(world_id: int):
    try:
        return to_payload(load_world(world_id))
    except LookupError:
        raise HTTPException(status_code=403, detail="World not found")

@app.put("/api/editor/save-world")
def save_world(request: SaveWorldPayload, user=Depends(require_user)):
    data = to_data(request)
    colour = base64.b64decode(request.colour)
    try:
        map_png = rgba_to_png(
            colour,
            data.width,
            data.height,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    
    worlds.upsert_save(
        name=data.name, 
        description=data.description,
        owner_id=user["id"],
        width=data.width,
        height=data.height,
        biome=data.biome,
        elevation=data.elevation,
        region=data.region,
        map_png=map_png,
        biome_lookup=data.biome_lookup,
        story_setup=data.story_setup,
        region_lookup=data.region_lookup,
        detail_lookup=data.detail_lookup,
        component_lookup=data.component_lookup,
        detail=data.detail,
        component=data.component
    )

def rgba_to_png(rgba: bytes, width: int, height: int) -> bytes:
    expected = width * height * 4
    if len(rgba) != expected:
        raise ValueError(f"expected {expected} bytes for {width}x{height}, got {len(rgba)}")

    image = Image.frombytes("RGBA", (width, height), rgba)
    buffer = io.BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()
