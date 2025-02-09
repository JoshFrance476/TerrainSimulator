import numpy as np
from scipy.ndimage import binary_dilation

def generate_coastline_map(elevation_map):
    """
    Generates a coastline map where coastlines are black and everything else is white.
    
    Coastlines are identified as locations where positive and negative values are adjacent.
    
    Args:
        region_map (list of lists or numpy array): 2D terrain height map with positive (land) 
        and negative (water) values.

    Returns:
        numpy array: 3-channel image where coastlines are black (0,0,0) and everything else is white (255,255,255).
    """
    region_array = np.array(elevation_map)  # Convert to NumPy array for fast processing
    rows, cols = region_array.shape

    # Identify water (-) and land (+) using boolean masks
    water_mask = region_array < 0
    land_mask = region_array > 0

    # Create a structuring element (cross shape) for checking adjacent cells
    structuring_element = np.array([[0,1,0], [1,1,1], [0,1,0]])  # 4-way connectivity

    # Expand water mask to see where it overlaps with land
    water_expanded = binary_dilation(water_mask, structure=structuring_element)
    
    # Coastline occurs where land is adjacent to expanded water
    coastline_mask = water_expanded & land_mask  

    # Generate output image with white background
    coastline_map = np.full((rows, cols, 3), (255, 255, 255), dtype=np.uint8)  # White background
    
    # Mark coastlines in black
    coastline_map[coastline_mask] = (0, 0, 0)

    return coastline_map

import matplotlib.pyplot as plt
import matplotlib.cm as cm

def apply_heatmap_overlay(data_map, coastline_map, colormap="viridis", alpha=0.6):
    """
    Overlays a heatmap onto the coastline map based on the values in data_map.

    Args:
        data_map (2D NumPy array): A float array representing data to be displayed as a heatmap.
        coastline_map (3D NumPy array): The base image onto which the heatmap is applied.
        colormap (str): The matplotlib colormap to use (e.g., "hot", "viridis", "plasma").
        alpha (float): Opacity of the heatmap overlay (0 = transparent, 1 = solid).

    Returns:
        3D NumPy array: The coastline map with the heatmap overlay applied.
    """
    # Ensure data_map and coastline_map have the same shape
    if data_map.shape != coastline_map.shape[:2]:
        raise ValueError("data_map and coastline_map must have the same spatial dimensions!")

    # Normalize data_map values between 0 and 1
    data_min, data_max = np.min(data_map), np.max(data_map)
    if data_max > data_min:
        normalized_data = (data_map - data_min) / (data_max - data_min)
    else:
        normalized_data = np.zeros_like(data_map)  # Avoid divide-by-zero errors

    # Get the colormap and apply it to the normalized data
    cmap = cm.get_cmap(colormap)
    heatmap = cmap(normalized_data)[:, :, :3]  # Extract RGB channels (ignore alpha)

    # Convert heatmap values to 0-255 integer range
    heatmap = (heatmap * 255).astype(np.uint8)

    # Blend the heatmap onto the coastline_map (where data is nonzero)
    output_map = coastline_map.copy()
    for r in range(data_map.shape[0]):
        for c in range(data_map.shape[1]):
            if data_map[r, c] > 0:  # Only apply heatmap where there's data
                output_map[r, c] = (
                    (1 - alpha) * coastline_map[r, c] + alpha * heatmap[r, c]
                ).astype(np.uint8)

    return output_map



def generate_territory_overlay(display_map, territory_map, state_list, alpha=0.6):
    """
    Applies a color overlay to display_map based on territory ownership.

    Args:
        display_map (numpy array): 3D array representing the terrain image (rows, cols, RGB).
        territory_map (numpy array): 2D array where each cell contains a city UID or 0 for unclaimed.
        cities_list (list of City objects): List of City objects, each with a UID and a color.
        alpha (float): Blending factor (0 = no change, 1 = full city color).

    Returns:
        numpy array: The modified display map with territories overlaid.
    """

    # Step 1: Create a UID-to-Color mapping from cities_list
    city_colors = {state.sid: np.array(state.colour) for state in state_list}

    # Step 2: Initialize an overlay with the same shape as display_map
    overlay = display_map.copy()

    # Step 3: Iterate over the territory_map and apply colors
    rows, cols = territory_map.shape
    for i in range(rows):
        for j in range(cols):
            id = territory_map[i, j]
            if id == -1:
                #Location is city
                overlay[i,j] = [0,0,0]
            elif id in city_colors:  # If the cell belongs to a city
                city_color = city_colors[id]

                # Blend city color with display_map color
                overlay[i, j] = (
                    (1 - alpha) * overlay[i, j] + alpha * city_color
                ).astype(np.uint8)

    return overlay
