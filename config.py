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

