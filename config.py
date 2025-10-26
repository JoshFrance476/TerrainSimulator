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
NUMBER_OF_RIVERS = 15
RIVER_SOURCE_MIN_ELEVATION = 0.65

STARTING_SETTLEMENT_COUNT = 0
SETTLEMENT_LIMIT = 30

SEED = random.randint(0,10000)

TOGGLE_LLM_EVENTS = True

LLM_THEME = "Star wars"

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

SETTLEMENT_TIERS = {
    0: "settlement",
    3: "village",
    4: "town",
    5: "city"
    }

LLM_ACTIONS = {
    "increase_population": {
        "low": {"population": + 10},
        "medium": {"population": + 20},
        "high": {"population": + 30}
    },
    "decrease_population": {
        "low": {"population": - 10},
        "medium": {"population": - 20},
        "high": {"population": - 30}
    },
    "increase_cohesion": {},
    "decrease_cohesion": {},
    "settlement_destruction": {},
    "rebellion": {},
    "regime_change": {},
}

LLM_ACTIONS_NAMES = list(LLM_ACTIONS.keys())

REGION_RULES = [
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
    1: (45.0, 1.0, 0.45),
    2: (60.0, 1.0, 0.85),
    3: (230.0, 0.0, 0.15),
    4: (230.0, 1.0, 0.706),
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
        "upgraded_bonuses": {"population_growth": 0.02},
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

SETTLEMENT_NAMES = [
    "Alderwyn",
    "Brackenreach",
    "Eldervale",
    "Stoneford",
    "Ravenmoor",
    "Willowmere",
    "Foxhollow",
    "Ashbourne",
    "Highmere",
    "Silverstead",
]