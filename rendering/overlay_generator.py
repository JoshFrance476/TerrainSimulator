import numpy as np
import matplotlib.cm as cm
from . import config


def apply_heatmap_overlay(coastline_map, data_map, colormap="viridis", alpha=0.6):
    """
    Overlays a heatmap onto the coastline map based on the values in data_map.

    Args:
        data_map (2D NumPy array): A float array representing data to be displayed as a heatmap.
        colormap (str): The matplotlib colormap to use (e.g., "hot", "viridis", "plasma").
        alpha (float): Opacity of the heatmap overlay (0 = transparent, 1 = solid).

    Returns:
        3D NumPy array: The coastline map with the heatmap overlay applied.
    """
    # Ensure data_map and coastline_map have the same shape
    if data_map.shape != coastline_map.shape:
        raise ValueError("data_map and coastline_map must have the same spatial dimensions!")

    base_map = np.full((*data_map.shape, 3), (255, 255, 255), dtype=np.uint8)  # White background

    #If elevation map, normalise to 0-1
    if data_map.min() == -1:
        data_map = (data_map + 1) / 2
    
    if data_map.max() > 10:
        data_map = (data_map - 1)/ 4


    # Get the colormap and apply it to the normalized data
    cmap = cm.get_cmap(colormap)
    heatmap = cmap(data_map)[:, :, :3]  # Extract RGB channels (ignore alpha)

    # Convert heatmap values to 0-255 integer range
    heatmap = (heatmap * 255).astype(np.uint8)
        
    output_map = ((1 - alpha) * base_map + alpha * heatmap).astype(np.uint8)

    output_map[coastline_map == 1] = (0, 0, 0) 

    # Set cells with with value 0 to white (sea)
    #mask = data_map == 0
    #output_map[mask] = (255, 255, 255)

    return output_map

