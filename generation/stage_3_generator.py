import numpy as np
from utils.map_utils import calculate_proximity_map
from biome_config import biome_config, biome_to_id
from skimage.segmentation import find_boundaries
from skimage.morphology import skeletonize
from config import SEA_LEVEL


def generate_stage_3(river_map, sea_map, elevation_map, temperature_map, rainfall_map, steepness_map):

    river_proximity_map = calculate_proximity_map(river_map)
    sea_proximity_map = calculate_proximity_map(sea_map)

    region_map, region_boundary_map, region_label_map = determine_region(elevation_map, temperature_map, rainfall_map)
    fertility_map = calculate_soil_fertility(region_map, rainfall_map, elevation_map, temperature_map)
    traversal_cost_map = calculate_traversal_cost(region_map, steepness_map)            

    return river_proximity_map, sea_proximity_map, region_map, fertility_map, traversal_cost_map, region_boundary_map, region_label_map





def calculate_traversal_cost(region_map, steepness_map):
    #cost_lookup = REGION_COST_LOOKUP[region_map]

    #steepness_cost = steepness_map * STEEPNESS_MULTIPLIER_ON_TRAVERSAL_COST
    #traversal_cost_map = cost_lookup + steepness_cost

    traversal_cost_map = np.zeros_like(region_map, dtype=np.int8)

    return traversal_cost_map




def calculate_soil_fertility(region, rainfall, elevation, temperature):
    """
    Determines soil fertility based on rainfall, elevation, temperature and region.
    """
    fertility = rainfall.copy()

    fertility[elevation > 0.7] *= 0.1
    fertility[elevation < 0.2] *= 1.2

    fertility[region == biome_to_id['ocean']] = 0
    fertility[region == biome_to_id['desert']] *= 0.1
    fertility[region == biome_to_id['arid']] *= 0.4
    fertility[region == biome_to_id['mountains']] *= 0.1
    fertility[region == biome_to_id['snowy peaks']] *= 0.05
    fertility[region == biome_to_id['marsh']] *= 0.5
    fertility[region == biome_to_id['savanna']] *= 0.5
    fertility[region == biome_to_id['grassland']] *= 1.2



    weight = 1.0 - (temperature - 0.5)**2 * 4
    weight = np.clip(weight, 0, 1)   
    fertility *= weight

    min_val = fertility.min()
    max_val = fertility.max()
    fertility = (fertility - min_val) / (max_val - min_val + 1e-9)

    return fertility




def determine_region(elevation, temperature, rainfall):
    """
    Assigns biome IDs using discrete (elevation, temperature, rainfall) bins
    defined in biome_config. Each cell is classified based on which bin it falls into.
    Elevation < SEA_LEVEL → 0
    Elevation ≥ SEA_LEVEL → quantized into 1-4.
    """

    region_map = np.full(elevation.shape, -1, dtype=np.int8)
    region_label_map = np.full(elevation.shape, -1, dtype=np.int8)

    # Quantize temperature and rainfall into 0–4
    def quantize(value):
        return np.clip((value * 5).astype(int), 0, 4)

    t_idx = quantize(temperature)
    r_idx = quantize(rainfall)

    # Special quantization for elevation
    e_idx = np.zeros_like(elevation, dtype=np.int8)
    above_sea = elevation >= SEA_LEVEL
    e_scaled = (elevation[above_sea] - SEA_LEVEL) / (1 - SEA_LEVEL)
    e_idx[above_sea] = np.clip((e_scaled * 4).astype(int) + 1, 1, 4)


    # Assign biomes
    for e in range(5):
        for t in range(5):
            for r in range(5):
                biome = biome_config.get((e, t, r))
                if biome is None:
                    continue
                mask = (e_idx == e) & (t_idx == t) & (r_idx == r)
                region_map[mask] = biome_to_id[biome]

                label_id = e * 25 + t * 5 + r
                region_label_map[mask] = label_id
    
    region_boundary_map = find_boundaries(region_label_map, mode='outer')


    return region_map, region_boundary_map, region_label_map







