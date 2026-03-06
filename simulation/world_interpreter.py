from skimage.segmentation import quickshift
from utils.colour_utils import hsv_to_rgb_array
from simulation.region_manager import RegionManager
import numpy as np

class WorldInterpreter:
    def __init__(self, colour_map, biome_map):
        self.chunk_manager = RegionManager()
        self.chunked_map = None
        self.colour_map = colour_map
        self.biome_map = biome_map

        self.generate_biome_chunk_map()
    
    def get_chunk_map(self):
        return self.chunk_manager.get_region_map()
    
    def generate_biome_chunk_map(self):
        colour_map = self.colour_map
        biome_map = self.biome_map
        ocean_mask = (biome_map == 0)

        colour_map[ocean_mask] = (0,0,0)
        rgb_colour_map = hsv_to_rgb_array(colour_map)

        # Chunking algorithm
        chunked_map = quickshift(rgb_colour_map, kernel_size=1, max_dist=5, ratio=0.2)

        chunked_map[ocean_mask] = -1

        ids = np.unique(chunked_map)
        ids = ids[ids != -1]
        for id in ids:
            chunk_mask = chunked_map == id
            rid = self.chunk_manager.create_region()
            self.chunk_manager.add_region_with_mask(chunk_mask, rid)
        self.chunked_map = chunked_map
    
    def get_location_interpretation(self):
        # Intepretation algorithm
        interpretation = ""

        return interpretation