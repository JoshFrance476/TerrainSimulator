import numpy as np
from skimage.segmentation import quickshift
from skimage.measure import regionprops, label
from utils.colour_utils import hsv_to_rgb_array

class ChunkManager:
    def __init__(self, rows, cols, colour_map, biome_map):
        self.chunk_map = np.full((rows, cols), -1, dtype=np.int16)
        self.chunks = {}

        self.generate_chunk_map(colour_map, biome_map)

    def get_local_chunks(self, location, radius = 3):
        h, w = self.chunk_map.shape

        # Limit search to a bounding box for efficiency
        r0 = max(0, location[0] - radius)
        r1 = min(h, location[0] + radius + 1)
        c0 = max(0, location[1] - radius)
        c1 = min(w, location[1] + radius + 1)

        submap = self.chunk_map[r0:r1, c0:c1]

        # Coordinates relative to the submap
        yy, xx = np.ogrid[r0:r1, c0:c1]

        # Euclidean circle mask
        dist2 = (yy - location[0]) ** 2 + (xx - location[1]) ** 2
        mask = dist2 <= radius ** 2

        # Get unique chunk labels in the radius
        chunk_ids = np.unique(submap[mask])

        chunk_list = []
        for chunk_id in chunk_ids:
            chunk_list.append(self.chunks.get(int(chunk_id)))

        return chunk_list
    

    def get_closest_chunks(self, location, count=3):
        row, col = location
        results = []

        for chunk_id, chunk_data in self.chunks.items():
            if chunk_id == 0:
                continue

            coords = chunk_data["coords"]

            dy = coords[:, 0] - row
            dx = coords[:, 1] - col
            dist2 = dy * dy + dx * dx

            idx = np.argmin(dist2)
            min_dist2 = dist2[idx]

            nearest_row, nearest_col = coords[idx]
            direction = self.vector_to_direction(nearest_row - row, nearest_col - col)

            results.append({
                "id": chunk_id,
                "biome": self.biome_config.get_biome_name_from_id(chunk_data["biome"]),
                "distance": float(np.sqrt(min_dist2)),
                "direction": direction
            })

        results.sort(key=lambda x: x["distance"])
        return results[:count]

    def get_random_location_in_chunk(self, chunk_id):
        coords = self.chunks[chunk_id]["coords"]
        index = np.random.randint(0, len(coords))
        return coords[index]
    
    def get_semantic_surroundings(self, location):
        surrounding_chunks = self.get_closest_chunks(location, 5)
        description = ""
        for chunk in surrounding_chunks:
            description += f"ID: {chunk['id']}, Biome: {chunk['biome']}, Direction: {chunk['direction']}. "
        return description

    def vector_to_direction(self, dy, dx):
        if abs(dy) > abs(dx):
            return "north" if dy < 0 else "south"
        elif abs(dx) > abs(dy):
            return "east" if dx > 0 else "west"
        else:
            if dy < 0 and dx > 0: return "north-east"
            if dy < 0 and dx < 0: return "north-west"
            if dy > 0 and dx > 0: return "south-east"
            if dy > 0 and dx < 0: return "south-west"

    def generate_chunk_map(self, colour_map, biome_map):
        self.chunks = {}

        rgb_colour_map = hsv_to_rgb_array(colour_map)

        h, w = biome_map.shape
        chunk_map = np.zeros((h, w), dtype=np.int32)

        next_label = 1

        # Process each biome separately, excluding ocean
        biome_ids = np.unique(biome_map)
        biome_ids = biome_ids[biome_ids != 0]

        for biome_id in biome_ids:
            # Connected components for this biome only
            biome_regions = label(biome_map == biome_id, connectivity=1)

            for region in regionprops(biome_regions):
                minr, minc, maxr, maxc = region.bbox

                # Crop to region bounding box
                region_mask = (biome_regions[minr:maxr, minc:maxc] == region.label)
                region_rgb = rgb_colour_map[minr:maxr, minc:maxc].copy()

                region_rgb[~region_mask] = 0

                # Run quickshift on cropped area
                local_segments = quickshift(
                    region_rgb,
                    kernel_size=1,
                    max_dist=5,
                    ratio=0.2
                ).astype(np.int32)

                # Keep only labels inside the current biome region
                valid_labels = np.unique(local_segments[region_mask])

                for local_label in valid_labels:
                    mask = region_mask & (local_segments == local_label)
                    chunk_map[minr:maxr, minc:maxc][mask] = next_label

                    local_coords = np.argwhere(mask)
                    world_coords = local_coords + np.array([minr, minc])

                    self.chunks[next_label] = {
                        "biome": biome_id,
                        "coords": world_coords
                    }
                    next_label += 1

        self.chunks[0] = {
            "biome": 0
        }

        for chunk in regionprops(chunk_map):
            self.chunks[chunk.label]["centroid"] = chunk.centroid

        self.chunk_map = chunk_map
    
    def get_chunk_map(self):
        return self.chunk_map

    def get_id_at(self, location):
        return self.chunk_map[location]