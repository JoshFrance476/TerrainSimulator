import random

SEA_LEVEL = 0
NUMBER_OF_RIVERS = 10
RIVER_SOURCE_MIN_ELEVATION = 0.2

CAMERA_ROWS, CAMERA_COLS = 266, 466 
WORLD_ROWS, WORLD_COLS = CAMERA_ROWS * 2, CAMERA_COLS * 2
CELL_SIZE = 3 # Decreasing this by one increases generation time 4 fold
SCALE = 70 #Steepness is not synced with scale, will not be as obvious at more zoomed in levels
ELEVATION_IMPACT_ON_TEMP = 1
STEEPNESS_MULTIPLIER = 50


SEED = random.randint(0,10000)

SCREEN_WIDTH, SCREEN_HEIGHT = CAMERA_COLS * CELL_SIZE, CAMERA_ROWS * CELL_SIZE

NUMBER_OF_CITIES = 5
CITIES_MIN_DISTANCE = 14
CITY_MAX_TERRITORY = 50

LOD_THRESHOLD = 2.2  # Zoom threshold for switching LOD mode
ZOOM_STEP = 0.1  # Zoom increment step
PAN_STEP = 1    # Pan speed in pixels
MAX_ZOOM = 10
MIN_ZOOM = 1

SIDEBAR_WIDTH = 250  
FONT_SIZE = 18

STATE_COLOUR_PALETTE = [
    (0, 255, 0),   # Red
    (0, 180, 0),   # Green
    (0, 0, 180),   # Blue
    (180, 180, 0), # Yellow
    (180, 120, 0), # Orange
    (80, 0, 80),   # Purple
    (0, 180, 180), # Cyan
    (180, 20, 100) # Pink
]

REGION_CONDITIONS = [
    {"condition": lambda e, t, r, rp: e > 0.35, "color": "snowy peaks"},
    {"condition": lambda e, t, r, rp: e > 0.25, "color": "mountains"},
    {"condition": lambda e, t, r, rp: t < 0.02, "color": "tundra"},
    {"condition": lambda e, t, r, rp: e < 0.1 and t > 0.76 and r < 0.4, "color": "desert"},
    {"condition": lambda e, t, r, rp: e < 0.25 and t > 0.62 and r < 0.65 and rp >= 4, "color": "arid"},
    {"condition": lambda e, t, r, rp: e < 0.23 and t > 0.52 and (r > 0.5 or rp < 4), "color": "savannah"},
    {"condition": lambda e, t, r, rp: e < 0.05 and t < 0.45 and t > 0.2 and r > 0.6, "color": "marsh"},
    {"condition": lambda e, t, r, rp: r > 0.50, "color": "forest"},
    {"condition": lambda e, t, r, rp: True, "color": "grassland"},
]

REGION_COLORS = {
    "water": (0, 0, 180),
    "snowy peaks": (226, 226, 226),
    "mountains": (130, 130, 130),
    "desert": (194, 140, 70),
    "arid": (190, 160, 130),
    "grassland": (34, 139, 34),
    "forest": (34, 112, 34),
    "savannah": (125, 160, 50),
    "tundra": (230, 230, 230),
    "marsh": (0, 90, 0)
}

REGION_BASE_TRAVERSAL_COST = {
    "water": 10,
    "snowy peaks": 10,
    "mountains": 10,
    "desert": 1,
    "arid": 1,
    "grassland": 1,
    "forest": 1.2,
    "savannah": 1,
    "tundra": 2,
    "marsh": 2
}

REGIONS_TO_BLEND = {
    "desert": ["arid","savannah"],
    "arid": ["desert","savannah"],
    "grassland": ["forest", "marsh"],
    "forest": ["grassland", "marsh"],
    "savannah": ["desert","arid"]
}