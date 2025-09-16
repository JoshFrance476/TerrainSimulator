import numpy as np
from config import ELEVATION_IMPACT_ON_TEMP, TEMPERATURE_DEVIATION
from utils.map_utils import generate_perlin_noise_map

def generate_stage_1(rows, cols, scale, seed):
    elevation_map = generate_perlin_noise_map(rows, cols, scale*1.3, seed, False, 8, 0.38, 3.3)       
    rainfall_map = generate_perlin_noise_map(rows, cols, scale*2, seed*2, True, 5, 0.5, 2.2)    

    temperature_map = calculate_temperature(elevation_map, rows)  

    return elevation_map, rainfall_map, temperature_map



def calculate_temperature(elevation, rows):
    """
    Thank you ChatGPT for this function. Produces a bell curve temperature distribution.
    """
    row_idx = np.arange(elevation.shape[0])[:, None] / rows

    lat_factor = np.exp(-((row_idx - 0.5) ** 2) / (2 * TEMPERATURE_DEVIATION **2))

    base_temp = lat_factor

    temp = base_temp - (elevation * ELEVATION_IMPACT_ON_TEMP)

    temperature = np.clip(temp, 0, 1)

    return temperature.astype(np.float32)