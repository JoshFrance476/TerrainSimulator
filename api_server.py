"""
FastAPI adapter exposing the existing world/story backend to the web frontend.

Place this file in your project root (next to config.py) and run:

    pip install fastapi uvicorn pillow
    uvicorn api_server:app --reload --port 8000

It wraps your existing classes headlessly (no pygame loop):
  World, WorldEditor, BrushManager, StoryEngine, MapEntity
"""
import io
import threading
from pathlib import Path

import numpy as np
import yaml
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from PIL import Image
from pydantic import BaseModel

import config
from app.app_state import AppState, PaintMode
from editor.brush_manager import BrushManager
from editor.world_editor import WorldEditor
from storytelling.story_engine import StoryEngine
from utils.colour_utils import hsv_to_rgb_array
from world.map_entity import MapEntity
from world.world import World

app = FastAPI(title="World Studio API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

LOCK = threading.Lock()
SAVED_MAPS = Path("data/saved_maps")


class Backend:
    """Headless equivalent of AppController."""

    def __init__(self):
        self.world = World(config.WORLD_ROWS, config.WORLD_COLS)
        self.storyteller = StoryEngine(self.world)
        self.app_state = AppState()  # WorldEditor reads lctrl_down from it
        self.brush = BrushManager()
        self.editor = WorldEditor(self.world, self.brush, self.app_state)
        self.version = 0

        if config.MAP_NAME:
            try:
                self.load_map(config.MAP_NAME)
            except Exception:
                print("invalid map file name - generating procedural map")
                self.generate_map()
        else:
            self.generate_map()

    # -- lifecycle -------------------------------------------------------
    def bump(self):
        self.version += 1

    def _reset_player(self):
        self.player = MapEntity(
            location=self.world.get_starting_location(),
            boundary=(config.WORLD_ROWS, config.WORLD_COLS),
        )

    def generate_map(self):
        with open(SAVED_MAPS / "DefaultConfig.yaml") as f:
            biome_config = yaml.safe_load(f)
        self.world.load_data(biome_config)
        self.storyteller.clear_setup()
        self._reset_player()
        self.bump()

    def load_map(self, name):
        path = SAVED_MAPS / name
        with open(path / "story_setup.yaml") as f:
            self.storyteller.setup(yaml.safe_load(f))
        with open(path / "biome_config.yaml") as f:
            biome_config = yaml.safe_load(f)
        world_data = np.load(path / "map_data.npz", allow_pickle=True)
        rows, cols = world_data["biome"].shape
        config.WORLD_ROWS, config.WORLD_COLS = rows, cols
        self.world.rows, self.world.cols = rows, cols
        self.world.load_data(biome_config, world_data)
        self._reset_player()
        self.bump()

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
            yaml.dump(self.storyteller.get_setup(), f, sort_keys=False)

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
        scene = self.storyteller.get_current_scenario()
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
            "setup": self.storyteller.get_setup(),
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
    cell: list[int]


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
    with LOCK:
        B.editor.paint_mode = PaintMode.FILL if body.fill else PaintMode.BRUSH
        for cell in body.cells:
            loc = tuple(cell)
            if body.tool == "paint_biome":
                B.editor.paint_biome(loc, body.biome_id)
            elif body.tool == "elevate":
                B.editor.edit_elevation(loc, negative=body.negative)
            elif body.tool == "smooth":
                B.app_state.lctrl_down = True
                B.editor.edit_elevation(loc)
                B.app_state.lctrl_down = False
            elif body.tool == "region":
                if body.negative:
                    B.editor.remove_region(loc, body.region_id)
                else:
                    B.editor.paint_region(loc, body.region_id)
        B.bump()
    return {"version": B.version}


@app.get("/api/biomes")
def get_biomes():
    return B.world.get_biomes()


@app.post("/api/biomes")
def add_biome(body: BiomeBody):
    with LOCK:
        B.editor.add_biome(body.name, body.h, body.s, body.v,
                           body.traversal_cost, body.description)
        B.bump()
    return {"version": B.version}


@app.put("/api/biomes/{index}")
def edit_biome(index: int, body: BiomeBody):
    with LOCK:
        B.editor.edit_biome(index, body.name, body.h, body.s, body.v,
                            body.traversal_cost, body.description)
        B.bump()
    return {"version": B.version}


@app.post("/api/regions")
def create_region():
    with LOCK:
        rid = B.editor.create_region()
    return {"id": rid}


@app.put("/api/regions/{rid}")
def set_region_info(rid: int, body: RegionInfoBody):
    B.editor.set_painted_region_info(body.title, body.visible_desc,
                                     body.hidden_desc, rid)
    B.bump()
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
    B.storyteller.add_to_movement_history(
        {"direction": body.direction, "biome": biome})
    return {"player": list(B.player.get_location()), "biome": biome}


@app.post("/api/player/place")
def place_player(body: CellBody):
    B.player.set_location(tuple(body.cell))
    biome = B.world.get_biome_data_at_location(B.player.location)["name"]
    return {"player": list(B.player.get_location()), "biome": biome}


# ---------------------------------------------------------------- story
@app.get("/api/scene")
def get_scene():
    return {"scene": B.pending_json()}


@app.post("/api/scene/prompt")
def prompt_scene(body: CellBody):
    with LOCK:
        B.storyteller.generate_scene_interaction(tuple(body.cell))
    return {"scene": B.pending_json()}


@app.post("/api/scene/action")
def scene_action(body: IndexBody):
    scene = B.storyteller.get_current_scenario()
    if not scene or not scene.pending_interaction:
        raise HTTPException(409, "no pending interaction")
    actions = list(scene.pending_interaction.action_table.keys())
    if not 0 <= body.index < len(actions):
        raise HTTPException(400, "action index out of range")
    with LOCK:
        # NOTE: choose_action expects the action *string* (Scene.submit_action
        # keys into action_table) - the old pygame UI passed an index, which
        # was a latent bug.
        B.storyteller.choose_action(actions[body.index],
                                    tuple(B.player.get_location()))
        B.bump()  # scene summaries can write new regions into the world
    return {"scene": B.pending_json(),
            "history": B.storyteller.get_character_history()}


@app.post("/api/scene/custom")
def scene_custom(body: TextBody):
    scene = B.storyteller.get_current_scenario()
    if not scene or not scene.pending_interaction:
        raise HTTPException(409, "no pending interaction")
    with LOCK:
        # StoryEngine.submit_custom_action doesn't exist yet, so the adapter
        # registers the free-text action on the pending interaction and
        # resolves it through the normal pipeline.
        scene.pending_interaction.action_table[body.text] = {
            "exit_flag": False,
            "outcome": f"The player chose to: {body.text}",
        }
        B.storyteller.choose_action(body.text, tuple(B.player.get_location()))
        B.bump()
    return {"scene": B.pending_json()}


@app.post("/api/scene/exit")
def scene_exit():
    B.storyteller.clear_scenario()
    return {"ok": True}


@app.get("/api/character")
def get_character():
    return {
        "notebook": B.storyteller.get_notebook(),
        "stats": B.storyteller.state.stats,
        "history": B.storyteller.get_character_history(),
    }


@app.get("/api/story/setup")
def get_setup():
    return B.storyteller.get_setup()


@app.put("/api/story/setup")
def put_setup(body: SetupBody):
    B.storyteller.setup({
        "world_description": body.world_description,
        "character_description": body.character_description,
        "story_focus_description": body.story_focus_description,
    })
    return {"ok": True}


@app.post("/api/story/character-setup")
def character_setup():
    s = B.storyteller.state
    with LOCK:
        B.storyteller.setup_character(s.character_description,
                                      s.world_description,
                                      s.story_focus_description)
    return {"notebook": s.notebook, "stats": s.stats}


@app.get("/api/usage")
def get_usage():
    return {"usage": B.storyteller.get_token_usage()}


# ---------------------------------------------------------------- maps
@app.get("/api/maps")
def list_maps():
    if not SAVED_MAPS.exists():
        return {"maps": []}
    return {"maps": sorted(p.name for p in SAVED_MAPS.iterdir()
                           if p.is_dir() and (p / "map_data.npz").exists())}


@app.post("/api/maps/generate")
def maps_generate():
    with LOCK:
        B.generate_map()
    return {"version": B.version, "world": B.world_json()}


@app.post("/api/maps/save")
def maps_save(body: NameBody):
    with LOCK:
        B.save_map(body.name)
    return {"ok": True}


@app.post("/api/maps/load")
def maps_load(body: NameBody):
    with LOCK:
        try:
            B.load_map(body.name)
        except FileNotFoundError as e:
            raise HTTPException(404, str(e))
    return {"version": B.version, "world": B.world_json()}
