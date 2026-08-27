from models import WorldData
import numpy as np

from models import WorldData, Location, CellData, Region

class World:
    """Server-side representation of the world, with map layers as numpy arrays."""
    def __init__(self, world_data: WorldData):
        self.width = world_data.width
        self.height = world_data.height
        self.biome = np.frombuffer(world_data.biome, dtype=np.uint8).copy()
        self.elevation = np.frombuffer(world_data.elevation, dtype=np.uint8).copy()
        self.region = np.frombuffer(world_data.region, dtype=np.uint8).copy()
        self.biome_lookup = world_data.biome_lookup
        self.region_lookup = world_data.region_lookup
        self.detail = np.frombuffer(world_data.detail, dtype=np.uint8).copy()
        self.detail_lookup = world_data.detail_lookup
        self.component = np.frombuffer(world_data.component, dtype=np.uint8).copy()
        self.component_lookup = world_data.component_lookup

        self.max_regions_per_cell = 4
        self.no_region_sentinel = 255

    def _convert_coords_to_index(self, x, y):
        return y * self.width + x

    def get_cell_data(self, loc: Location) -> CellData:
        index = self._convert_coords_to_index(loc.x, loc.y)
        return CellData(
            biome=self._get_biome_name_from_id(self.biome[index]),
            detail=self._get_detail_name_from_id(self.detail[index]),
            component=self._get_component_name_from_id(self.component[index]),
            elevation=int(self.elevation[index]),
            regions=self._get_cell_regions(loc),
        )

    def _get_cell_regions(self, loc: Location) -> list[Region]:
        regions = []
        index = self._convert_coords_to_index(loc.x, loc.y)
        for i in range(self.max_regions_per_cell):
            region_id = self.region[index * self.max_regions_per_cell + i]
            if region_id == self.no_region_sentinel:
                break
            regions.append(self.region_lookup.get(str(region_id)))
        return regions

    def _get_biome_name_from_id(self, biome_id):
        return self.biome_lookup.get(str(biome_id))

    def _get_detail_name_from_id(self, detail_id):
        return self.detail_lookup.get(str(detail_id))

    def _get_component_name_from_id(self, component_id):
        return self.component_lookup.get(str(component_id))

