import numpy as np
import matplotlib.cm as cm
from utils import config

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

    output_map = ((1 - alpha) * coastline_map + alpha * heatmap).astype(np.uint8)

    # Set cells with with value 0 to white (sea)
    mask = data_map == 0
    output_map[mask] = (255, 255, 255)

    return output_map

