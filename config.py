import random
import numpy as np

LOGGING = True

CAMERA_ROWS, CAMERA_COLS = 57, 87
WORLD_ROWS, WORLD_COLS = CAMERA_ROWS*4, CAMERA_COLS*4
CELL_SIZE = 16 # Decreasing this by one increases generation time 4 fold
MAGNIFIER_CELL_SIZE = 10
MAGNIFIER_CELL_AMOUNT = 13
SCALE = 60 # Steepness is not synced with scale, will not be as obvious at more zoomed in levels

TEMPERATURE_DEVIATION = 0.16 # Smaller values = higher peak at equator, larger values = flatter curve
ELEVATION_IMPACT_ON_TEMP = 0.2
STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST = 1

SEA_LEVEL = 0.05
NUMBER_OF_RIVERS = 15
RIVER_SOURCE_MIN_ELEVATION = 0.65

REGION_BORDER_THICKNESS = 2

SEED = random.randint(0,10000)

TOGGLE_LLM_EVENTS = False

LLM_THEME = "Game of Thrones on a canonical map, but set 2000 years in the past. Stories should involve suprises and twists."

PAN_STEP = 1   # Pan speed in pixels


SIDEBAR_WIDTH = 250  
FONT_SIZE = 18

SCREEN_WIDTH, SCREEN_HEIGHT = CAMERA_COLS * CELL_SIZE + (SIDEBAR_WIDTH), CAMERA_ROWS * CELL_SIZE


BIOME_RULES = [
    {
        "name": "ocean",
        "colour": (240.0, 1.0, 0.706),
        "base_traversal_cost": 10,
        "conditions": [{
            "elevation": {"min": -1.0, "max": SEA_LEVEL}
        }]
    },
    {
        "name": "snowy peaks",
        "colour": (0.0, 0.0, 0.808),
        "base_traversal_cost": 10,
        "conditions": [{
            "elevation": {"min": 0.85, "max": 1.0},
            "temperature": {"min": 0.0, "max": 0.6}
        }]
    },
    {
        "name": "mountains",
        "colour": (0.0, 0.0, 0.471),
        "base_traversal_cost": 10,
        "conditions": [{
            "elevation": {"min": 0.7}
        }]
    },
    {
        "name": "glacier",
        "colour": (0.0, 0.0, 0.863),
        "base_traversal_cost": 5,
        "conditions": [{
            "temperature": {"max": 0.01}
        }]
    },
    {
        "name": "tundra",
        "colour": (105.0, 0.45, 0.471),
        "base_traversal_cost": 2,
        "conditions": [{
            "temperature": {"max": 0.09}
        }]
    },
    {
        "name": "desert",
        "colour": (30.0, 0.695, 0.643),
        "base_traversal_cost": 1,
        "conditions": [{
            "temperature": {"min": 0.8},
            "rainfall": {"max": 0.2}
        }]
    },
    {
        "name": "arid",
        "colour": (30.0, 0.375, 0.627),
        "base_traversal_cost": 1,
        "conditions": [{
            "temperature": {"min": 0.72},
            "rainfall": {"max": 0.6},
            "river_proximity": {"min": 4}
        }]
    },
    {
        "name": "savanna",
        "colour": (82.5, 0.636, 0.431), 
        "base_traversal_cost": 1,
        "conditions": [{
            "elevation": {"max": 0.5},
            "temperature": {"min": 0.55},
            "rainfall": {"min": 0.4},
        },
        {
            "elevation": {"max": 0.5},
            "temperature": {"min": 0.55},
            "river_proximity": {"max": 4}
        }]
    },
    {
        "name": "rainforest",
        "colour": (120.0, 1.0, 0.314),
        "base_traversal_cost": 1.5,
        "conditions": [{
            "elevation": {"max": 0.7},
            "temperature": {"min": 0.55},
            "rainfall": {"min": 0.7}
        }]
    },
    {
        "name": "marsh",
        "colour": (120.0, 1.0, 0.275),
        "base_traversal_cost": 2,
        "conditions": [{
            "elevation": {"max": 0.1},
            "temperature": {"min": 0.2, "max": 0.45},
            "rainfall": {"min": 0.8}
        }]
    },
    {
        "name": "forest",
        "colour": (120.0, 0.848, 0.361),
        "base_traversal_cost": 1,
        "conditions": [{
            "rainfall": {"min": 0.65}
        }]
    },
    {
        "name": "grassland",
        "colour": (112.9, 0.673, 0.431),
        "base_traversal_cost": 1,
        "conditions": [{
            "elevation": {"max": 0.7},
        }]
    },
    {
        "name": "river",
        "colour": (240.0, 0.68, 0.8),
        "base_traversal_cost": 5,
    },
    {
        "name": "farm",
        "colour": (60.0, 1.0, 0.85),
        "base_traversal_cost": 1,
    },
    {
        "name": "lumber mill",
        "colour": (45.0, 1.0, 0.45),
        "base_traversal_cost": 1,
    },
    {
        "name": "mine",
        "colour": (230.0, 0.0, 0.3),
        "base_traversal_cost": 1,
    },
    {
        "name": "fishing spot",
        "colour": (230.0, 1.0, 0.706),
        "base_traversal_cost": 1,
    }
]

BIOME_NAME_TO_ID = {r["name"]: idx for idx, r in enumerate(BIOME_RULES)}

BIOME_BY_NAME = {r["name"]: r for r in BIOME_RULES}

BIOME_COLOUR_LOOKUP = [r.get("colour") for r in BIOME_RULES]

BIOME_COST_LOOKUP = np.array(
    [r["base_traversal_cost"] for r in BIOME_RULES],
    dtype=np.float32
)
