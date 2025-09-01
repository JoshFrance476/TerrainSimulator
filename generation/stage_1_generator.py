from noise import pnoise2
import numpy as np
from utils.config import ELEVATION_IMPACT_ON_TEMP
import math

def generate_stage_1(rows, cols, scale, seed):
    elevation_map = generate_noise_map(rows, cols, scale, seed)       
    rainfall_map = generate_noise_map(rows, cols, scale*3, seed*2, True)    

    temperature_map = np.zeros((rows, cols), dtype=float)

    for r in range(rows):
        for c in range(cols):
            temperature_map[r][c] = calculate_temperature(elevation_map[r][c], r, rows)  
            #print(stage_1_map[r][c][0])

    return elevation_map, rainfall_map, temperature_map



def generate_noise_map(rows, cols, scale, seed, normalised=False):
    """
    Generate a noise map using Perlin noise.
    """
    noise_map = np.zeros((rows, cols), dtype=float)
    for r in range(rows):
        for c in range(cols):
            noise_value = pnoise2((r + seed) / scale, (c + seed) / scale, octaves=5, persistence=0.5, lacunarity=2.2)
            if (normalised == True):
                # Normalize the value to [0, 1]
                noise_value = (noise_value + 1) / 2
            noise_map[r][c] = noise_value
    return noise_map


def calculate_temperature(elevation, row, rows):
    """
    Calculate temperature based on elevation, normalized to [0, 1].
    """
    

    deviation = 0.18
    elevation_impact = ELEVATION_IMPACT_ON_TEMP
    # Apply a normal distribution to the latitude factor with peak at the middle
    lat_factor = math.exp(-((row / rows - 0.5) ** 2) / (2 * (deviation ** 2)))  # Normal distribution centered at 0.5
    base_temp = lat_factor  # Temperature range normalized to [0,1]
    alt_temp = base_temp - (elevation * elevation_impact)  # Elevation reduces temperature
    temperature = max(0, min(1, alt_temp))

    return temperature