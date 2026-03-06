import pygame
import config
import numpy as np

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


def produce_chunk_border_surface(chunk_map):
    rows, cols = chunk_map.shape

    cs = config.CELL_SIZE
    thickness = config.REGION_BORDER_THICKNESS
    surface = pygame.Surface((cols * cs, rows * cs), pygame.SRCALPHA)

    # Detect borders using vectorised comparisons
    left_border  = np.zeros_like(chunk_map, dtype=bool)
    right_border = np.zeros_like(chunk_map, dtype=bool)
    top_border   = np.zeros_like(chunk_map, dtype=bool)
    bot_border   = np.zeros_like(chunk_map, dtype=bool)

    left_border[:, 1:] = chunk_map[:, 1:] != chunk_map[:, :-1]
    right_border[:, :-1] = chunk_map[:, :-1] != chunk_map[:, 1:]
    top_border[1:, :] = chunk_map[1:, :] != chunk_map[:-1, :]
    bot_border[:-1, :] = chunk_map[:-1, :] != chunk_map[1:, :]

    ys, xs = np.nonzero(left_border | right_border | top_border | bot_border)

    for y, x in zip(ys, xs):
        rid = int(chunk_map[y, x])
        color = region_id_to_color(rid)

        px = x * cs
        py = y * cs

        if left_border[y, x]:
            pygame.draw.line(surface, color,
                             (px, py), (px, py + cs), thickness)

        if right_border[y, x]:
            pygame.draw.line(surface, color,
                             (px + cs, py), (px + cs, py + cs), thickness)

        if top_border[y, x]:
            pygame.draw.line(surface, color,
                             (px, py), (px + cs, py), thickness)

        if bot_border[y, x]:
            pygame.draw.line(surface, color,
                             (px, py + cs), (px + cs, py + cs), thickness)

    return surface