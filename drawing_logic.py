import pygame
import config

def get_hovered_cell(mouse_x, mouse_y, zoom_level, x_offset, y_offset, cell_size):
    """Converts screen coordinates to the corresponding grid cell considering zoom & pan."""

    # Convert screen coordinates to world coordinates
    world_x = (mouse_x + x_offset) / zoom_level
    world_y = (mouse_y + y_offset) / zoom_level

    # Convert world coordinates to grid cell indices
    cell_x = int(world_x // cell_size)
    cell_y = int(world_y // cell_size)

    return cell_y, cell_x

def draw_hover_highlight(screen, hovered_cell, x_offset, y_offset, zoom_level, cell_size, color=(255, 255, 255, 100)):
    """Draws a semi-transparent highlight over the hovered cell."""
    cell_y, cell_x = hovered_cell  # Ensure correct row/col order

    # Compute cell size after zooming
    scaled_cell_size = cell_size * zoom_level

    # Convert grid cell to screen coordinates (adjust for zoom & panning)
    screen_x = (cell_x * scaled_cell_size) - x_offset
    screen_y = (cell_y * scaled_cell_size) - y_offset

    # Ensure highlight surface has transparency
    highlight_surface = pygame.Surface((scaled_cell_size, scaled_cell_size), pygame.SRCALPHA)
    highlight_surface.fill(color)

    # Blit highlight onto the screen
    screen.blit(highlight_surface, (screen_x, screen_y))


def draw_terrain(display_map, screen, zoom_level, x_offset, y_offset, low_res_surface):
    """Draws terrain ensuring seamless tile alignment at all zoom levels."""
    if zoom_level > config.LOD_THRESHOLD:
        # High-detail mode (render individual cells)
        cell_size = config.CELL_SIZE * zoom_level  # Compute scaled tile size

        # Ensure integer-aligned offsets to prevent jittering
        x_offset_int = round(x_offset)
        y_offset_int = round(y_offset)

        for r in range(config.ROWS):
            for c in range(config.COLS):
                colour = display_map[r][c]

                # Convert grid position to screen position with integer alignment
                x = round(c * cell_size - x_offset_int)
                y = round(r * cell_size - y_offset_int)

                # Only render visible cells
                if -cell_size < x < config.WIDTH and -cell_size < y < config.HEIGHT:
                  pygame.draw.rect(screen, colour, (x, y, round(cell_size + 0.5), round(cell_size + 0.5)))
    else:
        # Low-detail mode (render entire surface)
        scaled_surface = pygame.transform.smoothscale(
            low_res_surface, (int(config.WIDTH * zoom_level), int(config.HEIGHT * zoom_level))
        )
        screen.blit(scaled_surface, (-x_offset, -y_offset))
