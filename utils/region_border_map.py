import pygame
import config

def region_id_to_color(region_id: int):
    r = (region_id * 97) % 256
    g = (region_id * 57) % 256
    b = (region_id * 17) % 256
    return (r, g, b, 255)


def produce_region_border_surface(region_map):
    rows = len(region_map)
    cols = len(region_map[0]) if rows else 0

    cs = config.CELL_SIZE
    surface = pygame.Surface((cols * cs, rows * cs), pygame.SRCALPHA)
    thickness = config.REGION_BORDER_THICKNESS

    for y in range(rows):
        for x in range(cols):
            cell_regions = region_map[y][x]
            if not cell_regions:
                continue

            px = x * cs
            py = y * cs

            left_regions  = region_map[y][x - 1] if x > 0 else set()
            right_regions = region_map[y][x + 1] if x < cols - 1 else set()
            top_regions   = region_map[y - 1][x] if y > 0 else set()
            bot_regions   = region_map[y + 1][x] if y < rows - 1 else set()

            for rid in cell_regions - left_regions:
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px, py), (px, py + cs), thickness)

            for rid in cell_regions - right_regions:
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px + cs, py), (px + cs, py + cs), thickness)

            for rid in cell_regions - top_regions:
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px, py), (px + cs, py), thickness)

            for rid in cell_regions - bot_regions:
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px, py + cs), (px + cs, py + cs), thickness)

    return surface