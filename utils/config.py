import random
import numpy as np

CAMERA_ROWS, CAMERA_COLS = 266, 466 
WORLD_ROWS, WORLD_COLS = CAMERA_ROWS * 2, CAMERA_COLS * 2
CELL_SIZE = 3 # Decreasing this by one increases generation time 4 fold
SCALE = 70 #Steepness is not synced with scale, will not be as obvious at more zoomed in levels
ELEVATION_IMPACT_ON_TEMP = 0.5
STEEPNESS_MULTIPLIER = 50

SEA_LEVEL = -0.05
NUMBER_OF_RIVERS = 20
RIVER_SOURCE_MIN_ELEVATION = 0.2

SEED = random.randint(0,10000)

SCREEN_WIDTH, SCREEN_HEIGHT = CAMERA_COLS * CELL_SIZE, CAMERA_ROWS * CELL_SIZE

PAN_STEP = 4    # Pan speed in pixels


SIDEBAR_WIDTH = 250  
FONT_SIZE = 18

REGION_LOOKUP = {
    "water": 0,
    "snowy peaks": 1,
    "mountains": 2,
    "desert": 3,
    "arid": 4,
    "grassland": 5,
    "forest": 6,
    "savannah": 7,
    "tundra": 8,
    "marsh": 9
}

REGION_NAMES = {v: k for k, v in REGION_LOOKUP.items()}


REGION_CONDITIONS = [
    {"condition": lambda e, t, r, rp: (e > 0.35), 
     "regionID": REGION_LOOKUP["snowy peaks"]},
    {"condition": lambda e, t, r, rp: (e > 0.25), 
     "regionID": REGION_LOOKUP["mountains"]},
    {"condition": lambda e, t, r, rp: (t < 0.02), 
     "regionID": REGION_LOOKUP["tundra"]},
    {"condition": lambda e, t, r, rp: (e < 0.1) & (t > 0.76) & (r < 0.4), 
     "regionID": REGION_LOOKUP["desert"]},
    {"condition": lambda e, t, r, rp: (e < 0.25) & (t > 0.62) & (r < 0.65) & (rp >= 4), 
     "regionID": REGION_LOOKUP["arid"]},
    {"condition": lambda e, t, r, rp: (e < 0.23) & (t > 0.52) & ((r > 0.5) | (rp < 4)), 
     "regionID": REGION_LOOKUP["savannah"]},
    {"condition": lambda e, t, r, rp: (e < 0.05) & (t < 0.45) & (t > 0.2) & (r > 0.6), 
     "regionID": REGION_LOOKUP["marsh"]},
    {"condition": lambda e, t, r, rp: (r > 0.50), 
     "regionID": REGION_LOOKUP["forest"]},
     {"condition": lambda e, t, r, rp: True, 
      "regionID": REGION_LOOKUP["grassland"]},
]



REGION_COLORS = {
    0: (0, 0, 180),
    1: (226, 226, 226),
    2: (130, 130, 130),
    3: (194, 140, 70),
    4: (190, 160, 130),
    5: (34, 139, 34),
    6: (34, 112, 34),
    7: (125, 160, 50),
    8: (230, 230, 230),
    9: (0, 90, 0)
}

REGION_BASE_TRAVERSAL_COST = np.array([
    10,  # 0 grassland
    10,  # 1 forest
    10,  # 2 desert
    1,   # 3 mountains
    1,   # 4 snowy peaks
    1,   # 5 tundra
    1,   # 6 savannah
    1,   # 7 arid
    2,   # 8 marsh
    2    # 9 water
], dtype=np.uint8)

REGIONS_TO_BLEND = {
    3: [4,7],
    4: [3,7],
    5: [6, 9],
    6: [5, 9],
    7: [3,4]
}