import numpy as np
from config import ELEVATION_IMPACT_ON_TEMP, TEMPERATURE_DEVIATION

def calculate_temperature(elevation, rows):
    """
    Thank you ChatGPT for this function. Produces a bell curve temperature distribution.
    """
    row_idx = np.arange(elevation.shape[0])[:, None] / rows

    lat_factor = np.exp(-((row_idx - 0.5) ** 2) / (2 * TEMPERATURE_DEVIATION **2))

    base_temp = lat_factor

    temp = base_temp - (elevation * ELEVATION_IMPACT_ON_TEMP)

    temperature = np.clip(temp, 0, 1)

    return temperature.astype(np.float32)