from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from sse_starlette.sse import EventSourceResponse

from pathlib import Path
import yaml
import numpy as np
from PIL import Image
import io
from pydantic import BaseModel
import uuid
from collections.abc import AsyncIterable

from backend.world.world import World
from backend.world.map_entity import MapEntity
from backend.storytelling.story_engine import StoryEngine
from app_state import PaintMode
from backend.editor.world_editor import WorldEditor
import config

from backend.utils.colour_utils import hsv_to_rgb_array

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

SAVED_MAPS = Path("backend/data/saved_maps")

class Backend:
    """A single object that holds all game state - replaces appController"""
    def __init__(self):
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS)
        self.story_engine = StoryEngine(self.world)
        self.editor = WorldEditor(self.world)

        self.version = 0

        if config.MAP_NAME:
            try:
                self.load_map(config.MAP_NAME)
            except Exception:
                print("invalid map file name - generating procedural map")
                self.generate_map()
        else:
            self.generate_map()
        
        
    def increment_version(self):
        self.version += 1
    
    def generate_map(self):
        with open(SAVED_MAPS / "default_config.yaml") as f:
            biome_config = yaml.safe_load(f)
        
        self.world.load_data(biome_config)

        self.story_engine.clear_setup()

        self.reset_player()

        self.increment_version()
    
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
        self.increment_version()

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
    def map_png(self):
        rgb = hsv_to_rgb_array(self.world.get_map_data("colour"))
        img = Image.fromarray(np.asarray(rgb, dtype=np.uint8))
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return buf.getvalue()

    def regions_json(self):
        region_map = self.world.get_region_map()
        cells = {}
        for r, row in enumerate(region_map):
            for c, ids in enumerate(row):
                for rid in ids:
                    cells.setdefault(rid, []).append([r, c])
        out = []
        for rid, cell_list in cells.items():
            region = self.world.get_region(rid)
            out.append({
                "id": rid,
                "title": getattr(region, "title", "") or f"Region {rid}",
                "visible_desc": getattr(region, "visible_desc", ""),
                "hidden_desc": getattr(region, "hidden_desc", ""),
                "cells": cell_list,
            })
        return out

    def pending_json(self):
        scene = self.story_engine.get_current_scene()
        if not scene:
            return None
        out = {
            "history": [
                {"situation": i.description, "action": i.chosen_action}
                for i in scene.completed_interactions
            ],
            "ended": scene.ended,
            "pending": None,
        }
        if scene.pending_interaction:
            p = scene.pending_interaction
            out["pending"] = {
                "description": p.description,
                "actions": [
                    {"action": a, "exit_flag": v["exit_flag"]}
                    for a, v in p.action_table.items()
                ],
            }
        return out

    def world_json(self):
        return {
            "rows": self.world.rows,
            "cols": self.world.cols,
            "player": list(self.player.get_location()),
            "version": self.version,
            "biomes": self.world.get_biomes(),
            "setup": self.story_engine.get_setup(),
        }

B = Backend()

# ---------------------------------------------------------------- models
class StrokeBody(BaseModel):
    tool: str                       # paint_biome | elevate | smooth | region
    cells: list[list[int]]
    biome_id: int | None = None
    region_id: int | None = None
    negative: bool = False
    fill: bool = False


class BrushBody(BaseModel):
    size: int | None = None
    strength: float | None = None
    elevation_updates_biome: bool | None = None


class BiomeBody(BaseModel):
    name: str
    h: float
    s: float
    v: float
    traversal_cost: float
    description: str = ""


class RegionInfoBody(BaseModel):
    title: str
    visible_desc: str = ""
    hidden_desc: str = ""


class SetupBody(BaseModel):
    world_description: str = ""
    character_description: str = ""
    story_focus_description: str = ""


class CellBody(BaseModel):
    x: int = 50
    y: int = 50


class TextBody(BaseModel):
    text: str


class IndexBody(BaseModel):
    index: int


class NameBody(BaseModel):
    name: str


class MoveBody(BaseModel):
    direction: str  # north | south | east | west


class PathBody(BaseModel):
    start: list[int]
    end: list[int]


active_streams: dict[str, str] = {}

# ---------------------------------------------------------------- story

from fastapi.responses import FileResponse

@app.get("/")
def get_index():
    return FileResponse("web_streaming_test.html")

@app.get("/api/scene")
def get_scene():
    return {"scene": B.pending_json()}


@app.post("/api/scene/prompt")
def prompt_scene(body: CellBody):
    stream_id = str(uuid.uuid4())

    active_streams[stream_id] = (body.x, body.y)

    return {"stream_id": stream_id}


@app.get("/stream")
async def stream_response(id: str) -> Response:
    cell = active_streams.pop(id, None)

    if not cell:
        raise HTTPException(status_code=404, detail="Stream ID not found")

    async def generate():
        async for event in B.story_engine.generate_scene_interaction(cell):
            yield event

    return EventSourceResponse(generate())

@app.post("/api/scene/action")
def scene_action(body: IndexBody):
    scene = B.story_engine.get_current_scene()
    if not scene or not scene.pending_interaction:
        raise HTTPException(409, "no pending interaction")
    actions = list(scene.pending_interaction.action_table.keys())
    if not 0 <= body.index < len(actions):
        raise HTTPException(400, "action index out of range")
    # NOTE: choose_action expects the action *string* (Scene.submit_action
    # keys into action_table) - the old pygame UI passed an index, which
    # was a latent bug.
    B.story_engine.choose_action(actions[body.index],
                                tuple(B.player.get_location()))
    B.increment_version()  # scene summaries can write new regions into the world
    return {"scene": B.pending_json(),
            "history": B.story_engine.get_character_history()}


@app.post("/api/scene/exit")
def scene_exit():
    B.story_engine.clear_scene()
    return {"ok": True}


@app.get("/api/character")
def get_character():
    return {
        "notebook": B.story_engine.get_notebook(),
        "stats": B.story_engine.state.stats,
        "history": B.story_engine.get_character_history(),
    }


@app.get("/api/story/setup")
def get_setup():
    return B.story_engine.get_setup()


@app.put("/api/story/setup")
def put_setup(body: SetupBody):
    B.story_engine.setup({
        "world_description": body.world_description,
        "character_description": body.character_description,
        "story_focus_description": body.story_focus_description,
    })
    return {"ok": True}


@app.post("/api/story/character-setup")
def character_setup():
    s = B.story_engine.state
    B.story_engine.setup_character(s.character_description,
                                    s.world_description,
                                    s.story_focus_description)
    return {"notebook": s.notebook, "stats": s.stats}


@app.get("/api/usage")
def get_usage():
    return {"usage": B.story_engine.get_token_usage()}


# ---------------------------------------------------------------- world
@app.get("/api/world")
def get_world():
    return B.world_json()


@app.get("/api/map.png")
def get_map_png(v: int = 0):
    return Response(B.map_png(), media_type="image/png",
                    headers={"Cache-Control": "no-store"})


@app.get("/api/regions")
def get_regions():
    return B.regions_json()


@app.get("/api/cell/{r}/{c}")
def get_cell(r: int, c: int):
    tile = B.world.get_tile_data_json((r, c))
    data = B.world.get_cell_data((r, c))
    tile["elevation"] = float(data["elevation"])
    tile["temperature"] = float(data["temperature"])
    tile["rainfall"] = float(data["rainfall"])
    tile["traversal_cost"] = float(data["traversal_cost"])
    return tile


@app.post("/api/path")
def get_path(body: PathBody):
    path = B.world.find_path(tuple(body.start), tuple(body.end))
    return {"path": [list(p) for p in (path or [])]}

# ---------------------------------------------------------------- editing
@app.post("/api/edit/brush")
def set_brush(body: BrushBody):
    if body.size is not None:
        B.brush.size = body.size
    if body.strength is not None:
        B.brush.strength = body.strength
    if body.elevation_updates_biome is not None:
        B.editor.elevation_updates_biome = body.elevation_updates_biome
    return {"ok": True}


@app.post("/api/edit/stroke")
def edit_stroke(body: StrokeBody):
    B.editor.paint_mode = PaintMode.FILL if body.fill else PaintMode.BRUSH
    for cell in body.cells:
        loc = tuple(cell)
        if body.tool == "paint_biome":
            B.editor.paint_biome(loc, body.biome_id)
        elif body.tool == "elevate":
            B.editor.edit_elevation(loc, negative=body.negative)
        elif body.tool == "smooth":
            B.editor.edit_elevation(loc)
        elif body.tool == "region":
            if body.negative:
                B.editor.remove_region(loc, body.region_id)
            else:
                B.editor.paint_region(loc, body.region_id)
    B.increment_version()
    return {"version": B.version}


@app.get("/api/biomes")
def get_biomes():
    return B.world.get_biomes()


@app.post("/api/biomes")
def add_biome(body: BiomeBody):
    B.editor.add_biome(body.name, body.h, body.s, body.v,
                        body.traversal_cost, body.description)
    B.increment_version()
    return {"version": B.version}


@app.put("/api/biomes/{index}")
def edit_biome(index: int, body: BiomeBody):
    B.editor.edit_biome(index, body.name, body.h, body.s, body.v,
                            body.traversal_cost, body.description)
    B.increment_version()
    return {"version": B.version}


@app.post("/api/regions")
def create_region():
    rid = B.editor.create_region()
    return {"id": rid}


@app.put("/api/regions/{rid}")
def set_region_info(rid: int, body: RegionInfoBody):
    B.editor.set_painted_region_info(body.title, body.visible_desc,
                                     body.hidden_desc, rid)
    B.increment_version()
    return {"version": B.version}


# ---------------------------------------------------------------- player
@app.post("/api/player/move")
def move_player(body: MoveBody):
    move = {"north": B.player.move_north, "south": B.player.move_south,
            "east": B.player.move_east, "west": B.player.move_west}
    if body.direction not in move:
        raise HTTPException(400, "direction must be north/south/east/west")
    move[body.direction]()
    biome = B.world.get_biome_data_at_location(B.player.location)["name"]
    B.story_engine.add_to_movement_history(
        {"direction": body.direction, "biome": biome})
    return {"player": list(B.player.get_location()), "biome": biome}


@app.post("/api/player/place")
def place_player(body: CellBody):
    B.player.set_location(tuple(body.cell))
    biome = B.world.get_biome_data_at_location(B.player.location)["name"]
    return {"player": list(B.player.get_location()), "biome": biome}


# ---------------------------------------------------------------- maps
@app.get("/api/maps")
def list_maps():
    if not SAVED_MAPS.exists():
        return {"maps": []}
    return {"maps": sorted(p.name for p in SAVED_MAPS.iterdir()
                           if p.is_dir() and (p / "map_data.npz").exists())}


@app.post("/api/maps/generate")
def maps_generate():
    B.generate_map()
    return {"version": B.version, "world": B.world_json()}


@app.post("/api/maps/save")
def maps_save(body: NameBody):
    B.save_map(body.name)
    return {"ok": True}


@app.post("/api/maps/load")
def maps_load(body: NameBody):
    try:
        B.load_map(body.name)
    except FileNotFoundError as e:
        raise HTTPException(404, str(e))
    return {"version": B.version, "world": B.world_json()}