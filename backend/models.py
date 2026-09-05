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
    detail: str | None
    component: str | None

@dataclass(frozen=True)
class StorySetup:
    world_description: str = ""
    story_description: str = ""
    character_description: str = ""

class StorylinePromptData(BaseModel):
    world_description: str
    story_description: str
    character_description: str
    region_lookup: dict
    component_lookup: dict


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
    temperature: float | None = None
    max_tokens: int | None = None
    reasoning_effort: str | None = None

class SaveWorldBody(BaseModel):
    name: str
    description: str = ""

class StartSessionBody(BaseModel):
    world_id: int | None = None

class SetupBody(BaseModel):
    world_description: str
    story_description: str
    character_description: str
    region_lookup: dict
    component_lookup: dict
    inventory: list
    stats: list[dict]
    notebook: list

class StorylinesSetupBody(BaseModel):
    world_description: str
    story_description: str
    character_description: str
    region_lookup: dict
    component_lookup: dict

class StorylinesBody(BaseModel):
    storylines: str

class SetupDescriptionsBody(BaseModel):
    character_description: str
    world_description: str
    story_description: str


class WorldData(BaseModel):
    """World data with map layers in bytes for server-side handling."""
    name: str
    description: str | None = None
    width: int
    height: int
    starting_location: dict
    biome: bytes
    elevation: bytes
    region: bytes
    biome_lookup: dict
    region_lookup: dict
    story_setup: dict
    detail_lookup: dict
    component_lookup: dict
    detail: bytes
    component: bytes

class WorldPayload(BaseModel):
    """World data with map layers base64-encoded for JSON transport."""
    name: str
    description: str | None = None
    width: int
    height: int
    starting_location: dict
    biome: str
    elevation: str
    region: str
    biome_lookup: dict
    story_setup: dict
    region_lookup: dict
    detail_lookup: dict
    component_lookup: dict
    detail: str
    component: str

class SaveWorldPayload(WorldPayload):
    colour: str

def to_payload(world: WorldData) -> WorldPayload:
    return WorldPayload(
        name=world.name,
        description=world.description,
        width=world.width,
        height=world.height,
        starting_location=world.starting_location,
        biome=base64.b64encode(world.biome).decode(),
        elevation=base64.b64encode(world.elevation).decode(),
        region=base64.b64encode(world.region).decode(),
        biome_lookup=world.biome_lookup,
        story_setup=world.story_setup,
        region_lookup=world.region_lookup,
        detail_lookup=world.detail_lookup,
        component_lookup=world.component_lookup,
        detail=base64.b64encode(world.detail).decode(),
        component=base64.b64encode(world.component).decode(),
    )

def to_data(payload: WorldPayload) -> WorldData:
    return WorldData(
        name=payload.name,
        description=payload.description,
        width=payload.width,
        height=payload.height,
        starting_location=payload.starting_location,
        biome=base64.b64decode(payload.biome),
        elevation=base64.b64decode(payload.elevation),
        region=base64.b64decode(payload.region),
        biome_lookup=payload.biome_lookup,
        story_setup=payload.story_setup,
        region_lookup=payload.region_lookup,
        detail_lookup=payload.detail_lookup,
        component_lookup=payload.component_lookup,
        detail=base64.b64decode(payload.detail),
        component=base64.b64decode(payload.component)
    )