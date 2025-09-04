import numpy as np
from scipy.ndimage import distance_transform_cdt
from noise import pnoise2

def find_x_largest_value_locations(data, x):
    x += 1
    flat_map = data.ravel()
    topk_indices = np.argpartition(flat_map, -x)[-x:]
    topk_indices_sorted = topk_indices[np.argsort(-flat_map[topk_indices])]

    rows, cols = data.shape
    coords = np.column_stack(np.unravel_index(topk_indices_sorted, (rows, cols)))
    return coords



def calculate_proximity_map(boolean_map):
    inverted_map = ~boolean_map

    proximity_map = distance_transform_cdt(inverted_map, metric="taxicab").astype(np.int16)

    return proximity_map


def generate_perlin_noise_map(rows, cols, scale, seed, only_positive=False):
    """
    Generate a noise map using Perlin noise.
    """
    noise_map = np.zeros((rows, cols), dtype=float)
    for r in range(rows):
        for c in range(cols):
            noise_value = pnoise2((r + seed) / scale, (c + seed) / scale, octaves=5, persistence=0.5, lacunarity=2.2)
            noise_map[r][c] = noise_value
    
    # Normalises map between 0 and 1
    min_val = noise_map.min()
    max_val = noise_map.max()
    if only_positive:
        noise_map = (noise_map - min_val) / (max_val - min_val)
    else:
        mid = (max_val + min_val) / 2.0
        half_range = (max_val - min_val) / 2.0
        noise_map = (noise_map - mid) / half_range

    return noise_map


def normalize(value, min_value, max_value):

    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0
