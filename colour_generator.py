import copy
import numpy as np


def generate_color_map(elevation_map, steepness_map, region_map, region_colours, regions_to_blend, blend_toggle = False, variation_toggle = True):
    rows = len(elevation_map)
    cols = len(elevation_map[0])
    
    if blend_toggle:
        colour_map = [[None for _ in range(cols)] for _ in range(rows)]
        colour_map = generate_smooth_color_map(region_map, region_colours, regions_to_blend)
    else:
        colour_map = [[region_colours[region_map[r][c]] for c in range(cols)] for r in range(rows)]

    for r in range(rows):
        for c in range(cols):
            elevation = elevation_map[r][c]
            steepness = steepness_map[r][c]

            final_color = colour_map[r][c]

            region = region_map[r][c]

            if (region == "water"):
                blend_factor = (elevation + 1) / 2  # Normalize to 0-1 range for water
                final_color = blend_colors(final_color, (190, 190, 255), blend_factor)
            elif variation_toggle:
                final_color = blend_colors(final_color, (0,0,0), steepness*1.4)
                final_color = blend_colors(final_color, (0,0,0), elevation/2)


            final_color = min(max(final_color[0], 0), 255), min(max(final_color[1], 0), 255), min(max(final_color[2], 0), 255)
            colour_map[r][c] = final_color
    return np.array(colour_map, dtype=np.uint8)




def blend_colors(color1, color2, factor):
    """
    Blend two colors based on a factor (0-1).
    """
    return tuple(int(c1 + (c2 - c1) * factor) for c1, c2 in zip(color1, color2))




def generate_smooth_color_map(region_map, region_colors, regions_to_blend, blend_factor=0.1, iterations=4):
    """
    Generate a smooth color map by blending neighboring regions iteratively.

    Args:
        region_map (list): 2D list of region strings.
        region_colors (dict): Dictionary mapping region names to RGB colors.
        blend_factor (float): The strength of blending between neighboring regions.
        iterations (int): Number of iterations to perform blending.

    Returns:
        list: 2D list of blended colors.
    """
    rows, cols = len(region_map), len(region_map[0])
    color_map = [[region_colors[region_map[r][c]] for c in range(cols)] for r in range(rows)]
    neighbor_offsets = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    

    for _ in range(iterations):
        
        new_color_map = copy.deepcopy(color_map)


        for r in range(rows):
            for c in range(cols):
                base_region = region_map[r][c]
                base_color = color_map[r][c]
                blended_color = list(base_color)

                if base_region not in regions_to_blend:
                    continue

                neighbors = [
                    color_map[r + dr][c + dc] for dr, dc in neighbor_offsets 
                    if 0 <= r + dr < rows and 0 <= c + dc < cols and region_map[r + dr][c + dc] in regions_to_blend[base_region]
                ]

                if neighbors:
                    for neighbor_color in neighbors:
                        blended_color = blend_colors(blended_color, neighbor_color, blend_factor)

                new_color_map[r][c] = tuple(blended_color)

        color_map = new_color_map

    return color_map
