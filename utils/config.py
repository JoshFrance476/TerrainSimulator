import random
import numpy as np

CAMERA_ROWS, CAMERA_COLS = 266, 440 
WORLD_ROWS, WORLD_COLS = CAMERA_ROWS*2, CAMERA_COLS*2
CELL_SIZE = 3 # Decreasing this by one increases generation time 4 fold
MAGNIFIER_CELL_SIZE = 6
MAGNIFIER_CELL_AMOUNT = 12
SCALE = 70 # Steepness is not synced with scale, will not be as obvious at more zoomed in levels

TEMPERATURE_DEVIATION = 0.16 # Smaller values = higher peak at equator, larger values = flatter curve
ELEVATION_IMPACT_ON_TEMP = 0.2
STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST = 1

SEA_LEVEL = 0.05
NUMBER_OF_RIVERS = 25
RIVER_SOURCE_MIN_ELEVATION = 0.6

STARTING_SETTLEMENT_COUNT = 1
SETTLEMENT_LIMIT = 30

SEED = random.randint(0,10000)


PAN_STEP = 4    # Pan speed in pixels


SIDEBAR_WIDTH = 250  
FONT_SIZE = 18

SCREEN_WIDTH, SCREEN_HEIGHT = CAMERA_COLS * CELL_SIZE + (SIDEBAR_WIDTH), CAMERA_ROWS * CELL_SIZE

STATE_COLOURS = {
    0: (255, 0, 0),
    1: (0, 255, 0),
    2: (0, 0, 255),
    3: (255, 255, 0),
    4: (0, 255, 255),
    5: (255, 0, 255),
    6: (255, 255, 255),
    7: (0, 0, 0),
    8: (128, 128, 128),
    9: (192, 192, 192),
    10: (255, 165, 0),
    
}



REGION_RULES = [
    {
        "name": "ocean",
        "colour": (0, 0, 180),
        "base_traversal_cost": 10,
        "conditions": [{
            "elevation": {"min": -1.0, "max": SEA_LEVEL}
        }]
    },
    {
        "name": "snowy peaks",
        "colour": (226, 226, 226),
        "base_traversal_cost": 10,
        "conditions": [{
            "elevation": {"min": 0.85, "max": 1.0},
            "temperature": {"min": 0.0, "max": 0.6}
        }]
    },
    {
        "name": "mountains",
        "colour": (150, 150, 150),
        "base_traversal_cost": 10,
        "conditions": [{
            "elevation": {"min": 0.7}
        }]
    },
    {
        "name": "glacier",
        "colour": (240, 240, 240),
        "base_traversal_cost": 5,
        "conditions": [{
            "temperature": {"max": 0.01}
        }]
    },
    {
        "name": "tundra",
        "colour": (100, 140, 86),
        "base_traversal_cost": 2,
        "conditions": [{
            "temperature": {"max": 0.09}
        }]
    },
    {
        "name": "desert",
        "colour": (194, 140, 80),
        "base_traversal_cost": 1,
        "conditions": [{
            "temperature": {"min": 0.8},
            "rainfall": {"max": 0.2}
        }]
    },
    {
        "name": "arid",
        "colour": (190, 160, 130),
        "base_traversal_cost": 1,
        "conditions": [{
            "temperature": {"min": 0.72},
            "rainfall": {"max": 0.6},
            "river_proximity": {"min": 4}
        }]
    },
    {
        "name": "savanna",
        "colour": (125, 140, 70),
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
        }
    ]},
    {
        "name": "rainforest",
        "colour": (20, 100, 20),
        "base_traversal_cost": 1.5,
        "conditions": [{
            "elevation": {"max": 0.7},
            "temperature": {"min": 0.55},
            "rainfall": {"min": 0.7}
        }]
    },
    {
        "name": "marsh",
        "colour": (0, 90, 0),
        "base_traversal_cost": 2,
        "conditions": [{
            "elevation": {"max": 0.1},
            "temperature": {"min": 0.2, "max": 0.45},
            "rainfall": {"min": 0.8}
        }]
    },
    {
        "name": "forest",
        "colour": (34, 112, 34),
        "base_traversal_cost": 1,
        "conditions": [{
            "rainfall": {"min": 0.65}
        }]
    },
    {
        "name": "grassland",
        "colour": (69, 130, 56),
        "base_traversal_cost": 1,
        "conditions": [{
            "elevation": {"max": 0.7},
        }]
    },
    {
        "name": "river",
        "colour": (100, 100, 255),
        "base_traversal_cost": 5,
    },
    {
        "name": "farm",
        "colour": (255, 255, 100),
        "base_traversal_cost": 1,
    },
    {
        "name": "lumber mill",
        "colour": (100, 100, 0),
        "base_traversal_cost": 1,
    },
    {
        "name": "mine",
        "colour": (40, 40, 40),
        "base_traversal_cost": 1,
    },
    {
        "name": "fishing spot",
        "colour": (0, 0, 255),
        "base_traversal_cost": 1,
    }
]

REGION_NAME_TO_ID = {r["name"]: idx for idx, r in enumerate(REGION_RULES)}

REGION_BY_NAME = {r["name"]: r for r in REGION_RULES}

REGION_COLOUR_LOOKUP = [r.get("colour") for r in REGION_RULES]

REGION_COST_LOOKUP = np.array(
    [r["base_traversal_cost"] for r in REGION_RULES],
    dtype=np.float32
)



RESOURCE_LOOKUP = {
    "none": 0,
    "lumber": 1,
    "fertile land": 2,
    "ore": 3,
    "fish": 4,
}

RESOURCE_NAMES = {v: k for k, v in RESOURCE_LOOKUP.items()}

RESOURCE_COLORS = {
    1: (100, 100, 0),
    2: (255, 255, 100),
    3: (40, 40, 40),
    4: (0, 0, 255),
}
"""
Resource rules function as follows:

'Region' - base probability of resource in given regions
'Factors' - 'min', 'max' - specify the value range where the resource can appear. 
            'weight' - specify the distribution of the resource within the range. 
                       0 = uniform distribution
                       >0 = more weight towards the max
                       <0 = more weight towards the min
"""
RESOURCE_RULES = {
    "lumber": {
        "upgraded": "lumber mill",
        "region": {"forest": 0.04},    
    },
    "fertile land": {
        "upgraded": "farm",
        "upgraded_bonuses": {"population_growth": 0.05},
        "region": {"grassland": 0.04, "savanna": 0.01},
        "fertility": {"min": 0.4, "max": 1, "weight": 1},
    },
    "ore": {
        "upgraded": "mine",
        "region": {"mountains": 0.01, "snowy peaks": 0.01},
    },
    "fish": {
        "upgraded": "fishing spot",
        "region": {"ocean": 0.01, "river": 0.02},
    },
}

