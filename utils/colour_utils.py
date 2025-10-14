import numpy as np
from config import REGION_COLOUR_LOOKUP, REGION_NAME_TO_ID

def generate_color_map(world_data, blend_toggle=False, variation_toggle=True):
    """
    Generates a color-coded terrain map based on elevation, biomes, and regions.
    """
    rows, cols = world_data['elevation'].shape
    colour_map = np.zeros((rows, cols, 3), dtype=np.float32)

    for r in range(rows):
        for c in range(cols):
            region_id = world_data['region'][r, c]
            color = REGION_COLOUR_LOOKUP[region_id]
            colour_map[r, c] = color

            if region_id == REGION_NAME_TO_ID["ocean"]:
                
                blend_factor = (min(world_data['elevation'][r, c],0) + 1) / 2  # Normalize to 0-1 range for water
                colour_map[r, c] = blend_colors(colour_map[r, c], (None,0,0), world_data['steepness'][r, c] * 0.2)
                colour_map[r, c] = blend_colors(colour_map[r, c], (None, 0.37, 1.0), blend_factor)


            elif variation_toggle:
                if region_id == REGION_NAME_TO_ID["mountains"]:
                    colour_map[r, c] = blend_colors(colour_map[r, c], (None,0,0), world_data['steepness'][r, c] * 0.3)
                    colour_map[r, c] = blend_colors(colour_map[r, c], (None,0,0.4), world_data['elevation'][r, c] / 2)


                else:
                    colour_map[r, c] = blend_colors(colour_map[r, c], (None,0,0.2), world_data['steepness'][r, c] * 0.3)
                    colour_map[r, c] = blend_colors(colour_map[r, c], (None,0,0.8), world_data['elevation'][r, c] / 4)



    return colour_map

def blend_colors(color1, color2, factor):
    """
    Blend two HSV colors directly.
    color1, color2 = (h, s, v) with h∈[0,360], s,v∈[0,1], or None to skip that channel.
    factor in [0,1].
    Returns HSV tuple.
    """
    h1, s1, v1 = color1
    h2, s2, v2 = color2

    # Blend only channels where color2 provides a value
    h = h1 if h2 is None else (1 - factor) * h1 + factor * h2
    s = s1 if s2 is None else (1 - factor) * s1 + factor * s2
    v = v1 if v2 is None else (1 - factor) * v1 + factor * v2

    return (h, s, v)



def hsv_to_rgb_array(hsv_map):
    """
    AI Generated function to convert HSV NumPy array to RGB.
    """
    h = hsv_map[..., 0] / 60.0  # 0–6
    s = hsv_map[..., 1]
    v = hsv_map[..., 2]

    c = v * s
    x = c * (1 - np.abs(h % 2 - 1))
    m = v - c

    # make a zero array with same shape
    z = np.zeros_like(c)

    # Prepare arrays
    rgb = np.zeros(hsv_map.shape, dtype=np.float32)

    conds = [
        (0 <= h) & (h < 1),
        (1 <= h) & (h < 2),
        (2 <= h) & (h < 3),
        (3 <= h) & (h < 4),
        (4 <= h) & (h < 5),
        (5 <= h) & (h < 6),
    ]

    rgb[conds[0]] = np.stack([c, x, z], axis=-1)[conds[0]]
    rgb[conds[1]] = np.stack([x, c, z], axis=-1)[conds[1]]
    rgb[conds[2]] = np.stack([z, c, x], axis=-1)[conds[2]]
    rgb[conds[3]] = np.stack([z, x, c], axis=-1)[conds[3]]
    rgb[conds[4]] = np.stack([x, z, c], axis=-1)[conds[4]]
    rgb[conds[5]] = np.stack([c, z, x], axis=-1)[conds[5]]

    rgb += m[..., None]  # add m to all channels
    rgb = (rgb * 255).astype(np.uint8)
    return rgb
