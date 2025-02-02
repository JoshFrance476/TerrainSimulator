import random

SEA_LEVEL = 0
NUMBER_OF_RIVERS = 10
RIVER_SOURCE_MIN_ELEVATION = 0.2
WIDTH, HEIGHT = 1400, 800
CELL_SIZE = 2 # Decreasing this by one increases generation time 4 fold
SCALE = 70 #Steepness is not synced with scale, will not be as obvious at more zoomed in levels
ELEVATION_IMPACT_ON_TEMP = 1


SEED = random.randint(0,10000)

ROWS, COLS = HEIGHT // CELL_SIZE, WIDTH // CELL_SIZE

NUMBER_OF_CITIES = 5

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
    "water": (0, 0, 255),
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