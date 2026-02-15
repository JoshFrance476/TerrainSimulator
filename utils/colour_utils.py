import numpy as np
import colorsys


def generate_color_map(world_data, biome_config, blend_toggle=False, variation_toggle=True):
    """
    This function has been vectorised by AI. Haven't reviewed the code, but it works and cuts run time by 80%. Original, non-vectorised function can be found in earlier commits if needed.
    """
    elevation = world_data["elevation"]
    steepness = world_data["steepness"]
    biome = world_data["biome"]

    rows, cols = elevation.shape

    colour_map = biome_config.colour_lookup[biome]

    # -------------------------
    # 2. Masks
    # -------------------------
    ocean_id = biome_config.name_to_id["ocean"]
    mountains_id = biome_config.name_to_id["mountains"]

    ocean_mask = biome == ocean_id
    mountains_mask = biome == mountains_id
    land_mask = ~ocean_mask

    # -------------------------
    # 3. Ocean rules
    # -------------------------
    if ocean_mask.any():
        # (min(elev, 0) + 1) / 2
        blend_factor = (np.minimum(elevation, 0) + 1) / 2

        # A) blend with (None,0,0) using steepness*0.2
        f = steepness * 0.2
        out = colour_map[ocean_mask]
        new = np.zeros_like(out)
        new[..., 0] = out[..., 0]  # R stays
        new[..., 1] = 0.0
        new[..., 2] = 0.0
        colour_map[ocean_mask] = out * (1 - f[ocean_mask, None]) + new * f[ocean_mask, None]

        # B) blend with (None, 0.37, 1.0)
        out = colour_map[ocean_mask]
        new = np.zeros_like(out)
        new[..., 0] = out[..., 0]       # R stays
        new[..., 1] = 0.37
        new[..., 2] = 1.0
        colour_map[ocean_mask] = out * (1 - blend_factor[ocean_mask, None]) + new * blend_factor[ocean_mask, None]

    # -------------------------
    # 4. Variation rules for land
    # -------------------------
    if variation_toggle:

        # ----- Mountains -----
        if mountains_mask.any():
            # A) blend with (None, 0, 0) using steepness * 0.3
            f = steepness * 0.3
            out = colour_map[mountains_mask]
            new = np.zeros_like(out)
            new[..., 0] = out[..., 0]
            new[..., 1] = 0.0
            new[..., 2] = 0.0
            colour_map[mountains_mask] = out * (1 - f[mountains_mask, None]) + new * f[mountains_mask, None]

            # B) blend with (None, 0, 0.4) using elevation / 2
            f = elevation / 2
            out = colour_map[mountains_mask]
            new = np.zeros_like(out)
            new[..., 0] = out[..., 0]
            new[..., 1] = 0.0
            new[..., 2] = 0.4
            colour_map[mountains_mask] = out * (1 - f[mountains_mask, None]) + new * f[mountains_mask, None]

        # ----- Non-mountain land -----
        non_mtn_land_mask = land_mask & (biome != mountains_id)
        if non_mtn_land_mask.any():
            # A) blend with (None, 0, 0.2) using steepness * 0.3
            f = steepness * 0.3
            out = colour_map[non_mtn_land_mask]
            new = np.zeros_like(out)
            new[..., 0] = out[..., 0]
            new[..., 1] = 0.0
            new[..., 2] = 0.2
            colour_map[non_mtn_land_mask] = out * (1 - f[non_mtn_land_mask, None]) + new * f[non_mtn_land_mask, None]

            # B) blend with (None, 0, 0.8) using elevation / 4
            f = elevation / 4
            out = colour_map[non_mtn_land_mask]
            new = np.zeros_like(out)
            new[..., 0] = out[..., 0]
            new[..., 1] = 0.0
            new[..., 2] = 0.8
            colour_map[non_mtn_land_mask] = out * (1 - f[non_mtn_land_mask, None]) + new * f[non_mtn_land_mask, None]

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

def hsv2rgb(h,s,v):
        h = h / 360
        return tuple(round(i * 255) for i in colorsys.hsv_to_rgb(h,s,v))