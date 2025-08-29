import numpy as np
from utils.config import REGION_COLORS

def generate_color_map(elevation_data, region_data, steepness_data, blend_toggle=False, variation_toggle=True):
    """
    Generates a color-coded terrain map based on elevation, biomes, and regions.
    """
    rows, cols = elevation_data.shape
    colour_map = np.zeros((rows, cols, 3), dtype=np.uint8)

    for r in range(rows):
        for c in range(cols):
            region = list(REGION_COLORS)[region_data[r][c]]
            color = REGION_COLORS.get(region, (255, 128, 128))  # Default to pink
            colour_map[r, c] = color

            if region == "water":

                blend_factor = (elevation_data[r, c] + 1) / 2  # Normalize to 0-1 range for water
                colour_map[r, c] = blend_colors(colour_map[r, c], (190, 190, 255), blend_factor)


            elif variation_toggle:

                colour_map[r, c] = blend_colors(colour_map[r, c], (0,0,0), steepness_data[r, c] * 1.4)
                colour_map[r, c] = blend_colors(colour_map[r, c], (0,0,0), elevation_data[r, c] / 2)



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
