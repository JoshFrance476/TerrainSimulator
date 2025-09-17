import numpy as np
from config import REGION_COLOUR_LOOKUP, REGION_NAME_TO_ID

def generate_color_map(world_data, blend_toggle=False, variation_toggle=True):
    """
    Generates a color-coded terrain map based on elevation, biomes, and regions.
    """
    rows, cols = world_data['elevation'].shape
    colour_map = np.zeros((rows, cols, 3), dtype=np.uint8)

    for r in range(rows):
        for c in range(cols):
            region_id = world_data['region'][r, c]
            color = REGION_COLOUR_LOOKUP[region_id]
            colour_map[r, c] = color

            if region_id == REGION_NAME_TO_ID["ocean"]:
                
                blend_factor = (min(world_data['elevation'][r, c],0) + 1) / 2  # Normalize to 0-1 range for water
                colour_map[r, c] = blend_colors(colour_map[r, c], (0,0,0), world_data['steepness'][r, c] * 0.2)
                colour_map[r, c] = blend_colors(colour_map[r, c], (160, 160, 255), blend_factor)


            elif variation_toggle:
                if region_id == REGION_NAME_TO_ID["mountains"]:
                    colour_map[r, c] = blend_colors(colour_map[r, c], (0,0,0), world_data['steepness'][r, c] * 0.3)
                    colour_map[r, c] = blend_colors(colour_map[r, c], (100,100,100), world_data['elevation'][r, c] / 2)


                else:
                    colour_map[r, c] = blend_colors(colour_map[r, c], (50,50,50), world_data['steepness'][r, c] * 0.3)
                    colour_map[r, c] = blend_colors(colour_map[r, c], (200,200,200), world_data['elevation'][r, c] / 4)



    return colour_map

def blend_colors(color1, color2, factor):
    """
    Blends two colors based on a given factor.
    Ensures output values are clamped between 0 and 255.
    """
    return tuple(
        max(0, min(255, int(float(c1) + (float(c2) - float(c1)) * factor)))
        for c1, c2 in zip(color1, color2)
    )
