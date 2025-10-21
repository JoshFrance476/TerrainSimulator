import numpy as np
from scipy.ndimage import distance_transform_cdt, distance_transform_edt
from skimage.measure import regionprops, label
from skimage.segmentation import watershed
from skimage.morphology import binary_dilation
from noise import pnoise2

def find_x_largest_value_locations(data, x):
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


def generate_perlin_noise_map(rows, cols, scale, seed, only_positive=False, octaves=5, persistence=0.5, lacunarity=2.2):
    """
    Generate a noise map using Perlin noise.
    """
    noise_map = np.zeros((rows, cols), dtype=float)
    for r in range(rows):
        for c in range(cols):
            noise_value = pnoise2((r + seed) / scale, (c + seed) / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
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

def produce_landmass_label_map(land_map, ocean_label_map):
    land_map = ocean_label_map == 0
    label_map = label(land_map, connectivity=1)
    return label_map

def produce_water_body_label_map(map):
    label_map = label(map, connectivity=1)
    return label_map

def produce_continent_label_map(landmass_label_map):
    landmass_label_map = landmass_label_map
    continent_label_map = np.zeros_like(landmass_label_map)
    test_label_map = np.zeros_like(landmass_label_map)
    for region in regionprops(landmass_label_map):
        if region.area >= 200:
            region_mask = landmass_label_map == region.label
            distance = distance_transform_edt(region_mask)
            distance_mask = distance > 4
            distance_mask = binary_dilation(distance_mask)
            test_label_map[region_mask] = label(distance_mask)[region_mask]
            labels = watershed(region_mask, markers=label(distance_mask), mask=region_mask)
            continent_label_map[region_mask] = labels[region_mask]
    continent_label_map = label(continent_label_map)
    return continent_label_map, test_label_map

def produce_ocean_label_map(water_body_label_map):
    ocean_label_map = np.zeros_like(water_body_label_map)
    for region in regionprops(water_body_label_map):
        if region.area > 200:
            region_mask = water_body_label_map == region.label
            ocean_label_map[region_mask] = region.label
    return ocean_label_map

def produce_label_dict(label_map):
    label_dict = {}
    region_props = regionprops(label_map)
    for prop_list in region_props:
        label_dict[prop_list.label] = {
            'area':prop_list.area
        }
    return label_dict
