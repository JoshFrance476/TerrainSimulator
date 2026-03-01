import pygame
import config

def iter_set_bits(mask: int):
    """Yield bit indices that are set in mask."""
    while mask:
        lsb = mask & -mask
        bit = (lsb.bit_length() - 1)
        yield bit
        mask ^= lsb

def region_id_to_color(region_id: int):
    r = (region_id * 97) % 256
    g = (region_id * 57) % 256
    b = (region_id * 17) % 256
    return (r, g, b, 255)

def produce_region_border_surface(region_map):
    rows, cols = region_map.shape  # if numpy; otherwise use len(...)
    cs = config.CELL_SIZE
    surface = pygame.Surface((cols * cs, rows * cs), pygame.SRCALPHA)
    thickness = config.REGION_BORDER_THICKNESS

    for y in range(rows):
        for x in range(cols):
            m = int(region_map[y, x])
            if m == 0:
                continue

            px = x * cs
            py = y * cs

            # neighbor masks (0 at edges)
            ml = int(region_map[y, x - 1]) if x > 0 else 0
            mr = int(region_map[y, x + 1]) if x < cols - 1 else 0
            mt = int(region_map[y - 1, x]) if y > 0 else 0
            mb = int(region_map[y + 1, x]) if y < rows - 1 else 0

            # which region bits need a border on each side
            left_bits   = m & ~ml
            right_bits  = m & ~mr
            top_bits    = m & ~mt
            bottom_bits = m & ~mb

            # draw per-set-bit, preserving your per-region color scheme
            for rid in iter_set_bits(left_bits):
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px, py), (px, py + cs), thickness)

            for rid in iter_set_bits(right_bits):
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px + cs, py), (px + cs, py + cs), thickness)

            for rid in iter_set_bits(top_bits):
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px, py), (px + cs, py), thickness)

            for rid in iter_set_bits(bottom_bits):
                pygame.draw.line(surface, region_id_to_color(rid),
                                 (px, py + cs), (px + cs, py + cs), thickness)

    return surface