import config
import pygame

def produce_region_border_surface(region_map):
    rows = len(region_map)
    cols = len(region_map[0]) if rows > 0 else 0

    cs = config.CELL_SIZE
    map_width_px  = cols * cs
    map_height_px = rows * cs

    surface = pygame.Surface(
        (map_width_px, map_height_px),
        pygame.SRCALPHA
    )

    thickness = config.REGION_BORDER_THICKNESS

    for y in range(rows):
        for x in range(cols):
            cell_regions = region_map[y][x]
            if not cell_regions:
                continue

            px = x * cs
            py = y * cs

            for region_id in cell_regions:
                color = region_id_to_color(region_id)

                # Left
                if (
                    x == 0 or
                    region_id not in region_map[y][x - 1]
                ):
                    pygame.draw.line(
                        surface, color,
                        (px, py), (px, py + cs),
                        thickness
                    )

                # Right
                if (
                    x == cols - 1 or
                    region_id not in region_map[y][x + 1]
                ):
                    pygame.draw.line(
                        surface, color,
                        (px + cs, py), (px + cs, py + cs),
                        thickness
                    )

                # Top
                if (
                    y == 0 or
                    region_id not in region_map[y - 1][x]
                ):
                    pygame.draw.line(
                        surface, color,
                        (px, py), (px + cs, py),
                        thickness
                    )

                # Bottom
                if (
                    y == rows - 1 or
                    region_id not in region_map[y + 1][x]
                ):
                    pygame.draw.line(
                        surface, color,
                        (px, py + cs), (px + cs, py + cs),
                        thickness
                    )

    return surface

def region_id_to_color(region_id):
    # Simple hash → RGB (stable, distinct)
    r = (region_id * 97) % 256
    g = (region_id * 57) % 256
    b = (region_id * 17) % 256
    return (r, g, b, 255)
