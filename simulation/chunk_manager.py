import numpy as np
from skimage.segmentation import quickshift
from skimage.measure import regionprops
from utils.colour_utils import hsv_to_rgb_array

class ChunkManager:
    def __init__(self, rows, cols):
        self.chunk_map = np.ndarray((rows, cols), dtype=np.int16)
        self.chunks = {}

    
    def generate_chunk_map(self, colour_map, biome_map):
        ocean_mask = (biome_map == 0)

        colour_map[ocean_mask] = (0,0,0)
        rgb_colour_map = hsv_to_rgb_array(colour_map)

        # Chunking algorithm
        chunked_map = quickshift(rgb_colour_map, kernel_size=1, max_dist=5, ratio=0.2)

        chunked_map[ocean_mask] = -1

        chunk_props = regionprops(chunked_map)

        for chunk in chunk_props:
            self.chunks[chunk.label] = chunk.area
        
        self.chunk_map = chunked_map
    
    def get_chunk_map(self):
        return self.chunk_map

    def get_id_at(self, location):
        return self.chunk_map[location]