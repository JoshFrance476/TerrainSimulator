example_biome_config = {
    (0, 0, 0): "ocean", #Below sea level elevation, very low temperature and rainfall
    (1, 0, 0): "tundra", #Very low elevation, temperature and rainfall
    (1, 4, 0): "desert", #Very low elevation and rainfall, very high temperature
    (2, 4, 0): "desert" #Desert also at moderately low elevation
}

"""
(elevation, temperature, rainfall)
for elevation:
0 - Below sea level (-1 - 1)
1 - Very low (0-0.25)
2 - Moderately low (0.25-0.5)
3 - Moderately high (0.5-0.75)
4 - Very high (0.75-1)

for temperature and rainfall:
0 - Very low (0-0.2)
1 - Moderately low (0.2-0.4)
2 - Moderate (0.4-0.6)
3 - Moderately high (0.6-0.8)
4 - Very high (0.8-1)
"""

biome_config = {
    # Elevation 0: Below sea level
    (0, 0, 0): "ocean", (0, 0, 1): "ocean", (0, 0, 2): "ocean", (0, 0, 3): "ocean", (0, 0, 4): "ocean",
    (0, 1, 0): "ocean", (0, 1, 1): "ocean", (0, 1, 2): "ocean", (0, 1, 3): "ocean", (0, 1, 4): "ocean",
    (0, 2, 0): "ocean", (0, 2, 1): "ocean", (0, 2, 2): "ocean", (0, 2, 3): "ocean", (0, 2, 4): "ocean",
    (0, 3, 0): "ocean", (0, 3, 1): "ocean", (0, 3, 2): "ocean", (0, 3, 3): "ocean", (0, 3, 4): "ocean",
    (0, 4, 0): "ocean", (0, 4, 1): "ocean", (0, 4, 2): "ocean", (0, 4, 3): "ocean", (0, 4, 4): "ocean",

    # Elevation 1: Very low
    (1, 0, 0): "tundra", (1, 0, 1): "tundra", (1, 0, 2): "tundra", (1, 0, 3): "tundra", (1, 0, 4): "tundra",
    (1, 1, 0): "tundra", (1, 1, 1): "tundra", (1, 1, 2): "grassland", (1, 1, 3): "marsh", (1, 1, 4): "marsh",
    (1, 2, 0): "grassland", (1, 2, 1): "grassland", (1, 2, 2): "grassland", (1, 2, 3): "forest", (1, 2, 4): "forest",
    (1, 3, 0): "desert", (1, 3, 1): "arid", (1, 3, 2): "savanna", (1, 3, 3): "forest", (1, 3, 4): "rainforest",
    (1, 4, 0): "desert", (1, 4, 1): "desert", (1, 4, 2): "savanna", (1, 4, 3): "rainforest", (1, 4, 4): "rainforest",

    # Elevation 2: Moderately low
    (2, 0, 0): "tundra", (2, 0, 1): "tundra", (2, 0, 2): "tundra", (2, 0, 3): "grassland", (2, 0, 4): "forest",
    (2, 1, 0): "tundra", (2, 1, 1): "grassland", (2, 1, 2): "grassland", (2, 1, 3): "forest", (2, 1, 4): "forest",
    (2, 2, 0): "grassland", (2, 2, 1): "grassland", (2, 2, 2): "forest", (2, 2, 3): "forest", (2, 2, 4): "rainforest",
    (2, 3, 0): "desert", (2, 3, 1): "arid", (2, 3, 2): "savanna", (2, 3, 3): "forest", (2, 3, 4): "rainforest",
    (2, 4, 0): "desert", (2, 4, 1): "arid", (2, 4, 2): "savanna", (2, 4, 3): "rainforest", (2, 4, 4): "rainforest",

    # Elevation 3: Moderately high
    (3, 0, 0): "glacier", (3, 0, 1): "tundra", (3, 0, 2): "tundra", (3, 0, 3): "tundra", (3, 0, 4): "tundra",
    (3, 1, 0): "tundra", (3, 1, 1): "tundra", (3, 1, 2): "grassland", (3, 1, 3): "forest", (3, 1, 4): "forest",
    (3, 2, 0): "grassland", (3, 2, 1): "grassland", (3, 2, 2): "forest", (3, 2, 3): "forest", (3, 2, 4): "forest",
    (3, 3, 0): "desert", (3, 3, 1): "arid", (3, 3, 2): "savanna", (3, 3, 3): "forest", (3, 3, 4): "rainforest",
    (3, 4, 0): "desert", (3, 4, 1): "arid", (3, 4, 2): "savanna", (3, 4, 3): "rainforest", (3, 4, 4): "rainforest",

    # Elevation 4: Very high
    (4, 0, 0): "snowy peaks", (4, 0, 1): "snowy peaks", (4, 0, 2): "snowy peaks", (4, 0, 3): "snowy peaks", (4, 0, 4): "snowy peaks",
    (4, 1, 0): "snowy peaks", (4, 1, 1): "snowy peaks", (4, 1, 2): "mountains", (4, 1, 3): "mountains", (4, 1, 4): "mountains",
    (4, 2, 0): "mountains", (4, 2, 1): "mountains", (4, 2, 2): "mountains", (4, 2, 3): "forest", (4, 2, 4): "forest",
    (4, 3, 0): "arid", (4, 3, 1): "arid", (4, 3, 2): "mountains", (4, 3, 3): "mountains", (4, 3, 4): "forest",
    (4, 4, 0): "desert", (4, 4, 1): "arid", (4, 4, 2): "mountains", (4, 4, 3): "forest", (4, 4, 4): "rainforest",
}

biome_colours = {
    "ocean": (240.0, 1.0, 0.706),
    "snowy peaks": (0.0, 0.0, 0.808),
    "mountains": (0.0, 0.0, 0.471),
    "glacier": (0.0, 0.0, 0.863),
    "tundra": (105.0, 0.45, 0.471),
    "desert": (30.0, 0.695, 0.643),
    "arid": (30.0, 0.375, 0.627),
    "savanna": (82.5, 0.636, 0.431),
    "rainforest": (120.0, 1.0, 0.314),
    "marsh": (120.0, 1.0, 0.275),
    "forest": (120.0, 0.848, 0.361),
    "grassland": (112.9, 0.673, 0.431),
}

 # Create biome <-> id mappings
unique_biomes = sorted(set(biome_config.values()))
id_to_biome = {i: name for i, name in enumerate(unique_biomes)}
biome_to_id = {v: k for k, v in id_to_biome.items()}