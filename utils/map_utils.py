import numpy as np
from scipy.ndimage import distance_transform_cdt
from noise import pnoise2

def find_k_largest_value_locations(data, k):
    flat_map = data.ravel()
    topk_indices = np.argpartition(flat_map, -k)[-k:]
    topk_indices_sorted = topk_indices[np.argsort(-flat_map[topk_indices])]

    return topk_indices_sorted



def calculate_proximity_map(boolean_map):
    inverted_map = ~boolean_map

    proximity_map = distance_transform_cdt(inverted_map, metric="taxicab").astype(np.int16)

    return proximity_map


def generate_perlin_noise_map(rows, cols, scale, seed, normalised=False):
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


def normalize(value, min_value, max_value):

    return (value - min_value) / (max_value - min_value) if max_value > min_value else 0
