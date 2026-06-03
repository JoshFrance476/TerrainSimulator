import numpy as np
from scipy.ndimage import distance_transform_cdt, distance_transform_edt
from skimage.measure import regionprops, label
from skimage.segmentation import watershed
from skimage.morphology import binary_dilation
from skimage.graph import merge_hierarchical
from opensimplex import noise2

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
            noise_value = noise2((r + seed) / scale, (c + seed) / scale, octaves=octaves, persistence=persistence, lacunarity=lacunarity)
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
    landmass_dict = {}

    landmass_label_map = label(land_map, connectivity=1)
    for landmass in regionprops(landmass_label_map):
        landmass_dict[landmass.label] = {
            'area': landmass.area
        }
    return landmass_label_map, landmass_dict


def produce_water_body_label_map(water_map):
    water_map = label(water_map, connectivity=1)
    water_body_dict = {}

    water_body_label_map = label(water_map, connectivity=1)
    for water_body in regionprops(water_body_label_map):
        water_body_dict[water_body.label] = {
            'area': water_body.area
        }
    return water_body_label_map, water_body_dict


def produce_continent_label_map(landmass_label_map, threshold):
    continent_label_map = np.zeros_like(landmass_label_map)
    continent_dict = {}

    continent_threshold = 400

    for landmass in regionprops(landmass_label_map):
        region_mask = landmass_label_map == landmass.label
        if landmass.area >= continent_threshold:
            distance = distance_transform_edt(region_mask)
            distance_mask = distance > threshold
            distance_mask = binary_dilation(distance_mask)
            labels = watershed(region_mask, markers=label(distance_mask), mask=region_mask)
            continent_label_map[region_mask] = labels[region_mask]
            for continent in regionprops(continent_label_map):
                continent_dict
        else:
            continent_label_map[region_mask] = landmass.label
            
    continent_label_map = label(continent_label_map)

    for continent in regionprops(continent_label_map):
            continent_dict[continent.label] = {
                'area': continent.area
            }
            if continent.area > continent_threshold:
                continent_dict['type'] = 'continent'
            else:
                continent_dict['type'] = 'island'

    return continent_label_map, continent_dict


def produce_ocean_label_map(water_body_label_map, threshold):
    ocean_label_map = np.zeros_like(water_body_label_map)
    ocean_dict = {}
    for region in regionprops(water_body_label_map):
        if region.area > threshold:
            region_mask = water_body_label_map == region.label
            ocean_label_map[region_mask] = region.label
    return ocean_label_map, ocean_dict


