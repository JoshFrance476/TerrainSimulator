from dataclasses import dataclass
from pydantic import BaseModel
import base64

@dataclass(frozen=True)
class Location:
    x: int
    y: int

@dataclass(frozen=True)
class Region:
    title: str
    visible_description: str
    hidden_description: str

@dataclass(frozen=True)
class CellData:
    biome: str
    elevation: int
    regions: list[Region]

@dataclass(frozen=True)
class StorySetup:
    world_description: str
    character_description: str
    story_focus_description: str

@dataclass(frozen=True)
class SceneContext:
    tile_data: CellData
    movement_history: dict
    character_notebook: dict
    story_setup: StorySetup


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

class SetupStoryBody(BaseModel):
    world_description: str
    character_description: str
    story_focus_description: str

class WorldData(BaseModel):
    """World data with map layers in bytes for server-side handling."""
    name: str
    description: str | None = None
    width: int
    height: int
    biome: bytes
    elevation: bytes
    region: bytes
    biome_lookup: dict
    region_lookup: dict
    story_setup: dict

class WorldPayload(BaseModel):
    """World data with map layers base64-encoded for JSON transport."""
    name: str
    description: str | None = None
    width: int
    height: int
    biome: str
    elevation: str
    region: str
    biome_lookup: dict
    story_setup: dict
    region_lookup: dict

class SaveWorldPayload(WorldPayload):
    colour: str

def to_payload(world: WorldData) -> WorldPayload:
    return WorldPayload(
        name=world.name,
        description=world.description,
        width=world.width,
        height=world.height,
        biome=base64.b64encode(world.biome).decode(),
        elevation=base64.b64encode(world.elevation).decode(),
        region=base64.b64encode(world.region).decode(),
        biome_lookup=world.biome_lookup,
        story_setup=world.story_setup,
        region_lookup=world.region_lookup,
    )

def to_data(payload: WorldPayload) -> WorldData:
    return WorldData(
        name=payload.name,
        description=payload.description,
        width=payload.width,
        height=payload.height,
        biome=base64.b64decode(payload.biome),
        elevation=base64.b64decode(payload.elevation),
        region=base64.b64decode(payload.region),
        biome_lookup=payload.biome_lookup,
        story_setup=payload.story_setup,
        region_lookup=payload.region_lookup,
    )