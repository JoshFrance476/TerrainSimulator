import random

LOGGING = True

TARGET_FPS = 60

CAMERA_ROWS, CAMERA_COLS = 57, 87
WORLD_ROWS, WORLD_COLS = CAMERA_ROWS*4, CAMERA_COLS*4

CELL_SIZE = 16 # Decreasing this by one increases generation time 4 fold

SIDEBAR_WIDTH = 250 

SCREEN_WIDTH, SCREEN_HEIGHT = CAMERA_COLS * CELL_SIZE + (SIDEBAR_WIDTH), CAMERA_ROWS * CELL_SIZE

SCALE = 60 # Steepness is not synced with scale, will not be as obvious at more zoomed in levels

TEMPERATURE_DEVIATION = 0.16 # Smaller values = higher peak at equator, larger values = flatter curve
ELEVATION_IMPACT_ON_TEMP = 0.2
STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST = 1

REGION_BORDER_THICKNESS = 2

SEED = random.randint(0,10000)

PAN_STEP = 1
SCROLL_SPEED = 15
 
FONT_SIZE = 18

INITIALISE_NOTEBOOK_AND_STATS = False

