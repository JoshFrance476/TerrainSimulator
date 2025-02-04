import pygame
import sys
import config
import numpy as np 
from simulator_main import simulate_init, simulate_loop
from ui_generator import draw_sidebar

font_path = "fonts/OldNewspaperTypes.ttf"

# Initialize Pygame
pygame.init()
font = pygame.font.Font(font_path, 24)
screen = pygame.display.set_mode((config.WIDTH, config.HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Terrain Generation")

# Zoom and Pan settings
zoom_level = 1.0  # 1.0 = normal zoom, < 1 = zoomed out, > 1 = zoomed in
x_offset, y_offset = 0, 0  # Pan offsets
ZOOM_STEP = 0.1  # Zoom increment step
PAN_STEP = 5    # Pan speed in pixels
LOD_THRESHOLD = 4  # Threshold for switching LOD mode
max_zoom = 10
min_zoom = 1

def label_cities(city_map, city_names, cell_size):
    city_count = 0
    for row in range(city_map.shape[0]):
        for col in range(city_map.shape[1]):
            if city_map[row][col]:  # If city exists at this location
                city_name = city_names[city_count % len(city_names)]
                city_count += 1

                # Render city name text
                text_surface = font.render(city_name, True, (0, 0, 0))
                text_rect = text_surface.get_rect(center=(
                    (col * cell_size + cell_size // 2) + 30,
                    (row * cell_size + cell_size // 2) + 18
                ))

                screen.blit(text_surface, text_rect)

def generate_low_res_map(display_map):
    """Creates a low-resolution map surface."""
    rows, cols = len(display_map), len(display_map[0])
    low_res_surface = pygame.Surface((cols * config.CELL_SIZE, rows * config.CELL_SIZE))
    for r in range(rows):
        for c in range(cols):
            pygame.draw.rect(low_res_surface, display_map[r][c], 
                             (c * config.CELL_SIZE, r * config.CELL_SIZE, config.CELL_SIZE, config.CELL_SIZE))
    return low_res_surface

def draw_terrain(display_map, screen, zoom_level, x_offset, y_offset, low_res_surface):
    """Draws terrain ensuring seamless tile alignment at all zoom levels."""
    if zoom_level > LOD_THRESHOLD:
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





def clamp_pan(x_offset, y_offset, zoom_level):
    """Clamp pan offset to ensure the terrain does not move out of bounds."""
    max_x = max(0, config.COLS * config.CELL_SIZE * zoom_level - config.WIDTH)
    max_y = max(0, config.ROWS * config.CELL_SIZE * zoom_level - config.HEIGHT)

    x_offset = max(0, min(x_offset, max_x))
    y_offset = max(0, min(y_offset, max_y))

    return x_offset, y_offset

def main():
    """Main function to run the terrain visualization."""
    global zoom_level, x_offset, y_offset  # Allow modification inside function

    filter = 0

    simulate_init()
    display_map = simulate_loop(filter)
    low_res_display_map = generate_low_res_map(display_map)  # Pre-rendered low-res map
    

    surface_to_render = low_res_display_map

    clock = pygame.time.Clock()

    city_names = [f"City {i+1}" for i in range(config.NUMBER_OF_CITIES)]

    render_update = True
    sim_update = True

    show_city_labels = True

    # Track dragging state
    dragging = False
    drag_start_x, drag_start_y = 0, 0

    tick = 0

    

    while True:
        mouse_x, mouse_y = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    show_city_labels = not show_city_labels
                elif event.key == pygame.K_2:
                    filter += 1
                    sim_update = True
                elif event.key == pygame.K_LEFT:  # Pan left
                    x_offset -= PAN_STEP
                elif event.key == pygame.K_RIGHT:  # Pan right
                    x_offset += PAN_STEP
                elif event.key == pygame.K_UP:  # Pan up
                    y_offset -= PAN_STEP
                elif event.key == pygame.K_DOWN:  # Pan down
                    y_offset += PAN_STEP
                render_update = True

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    dragging = True
                    drag_start_x, drag_start_y = pygame.mouse.get_pos()

            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button released
                    dragging = False

            elif event.type == pygame.MOUSEMOTION:
                if dragging:
                    # Get current mouse position
                    mouse_x, mouse_y = pygame.mouse.get_pos()

                    # Calculate movement delta
                    dx = mouse_x - drag_start_x
                    dy = mouse_y - drag_start_y

                    # Adjust offsets
                    x_offset -= dx
                    y_offset -= dy

                    # Update last mouse position
                    drag_start_x, drag_start_y = mouse_x, mouse_y

                    render_update = True

            elif event.type == pygame.MOUSEWHEEL:
                # Determine new zoom level while clamping within range
                zoom_amount = ZOOM_STEP * event.y
                new_zoom = min(max_zoom, max(min_zoom, zoom_level + zoom_amount))  # Keep zoom within bounds

                if new_zoom != zoom_level:
                    # Get world position before zoom
                    world_x_before = (mouse_x + x_offset) / zoom_level
                    world_y_before = (mouse_y + y_offset) / zoom_level

                    # Apply new zoom level
                    zoom_level = new_zoom

                    # Compute new offsets to keep the view stable
                    x_offset = world_x_before * zoom_level - mouse_x
                    y_offset = world_y_before * zoom_level - mouse_y

                    render_update = True
        
        
        


        # Clamp panning to prevent moving out of the map bounds
        x_offset, y_offset = clamp_pan(x_offset, y_offset, zoom_level)

        tick = (tick + 1) % 20

        if tick == 0:
            sim_update = True


        if sim_update:
            display_map = simulate_loop(filter)
            surface_to_render = generate_low_res_map(display_map)  # Pre-rendered low-res map
            render_update = True
            sim_update = False

        if render_update:
            screen.fill((0, 0, 0))  # Clear screen only when necessary
            draw_terrain(display_map, screen, zoom_level, x_offset, y_offset, surface_to_render)
            #if show_city_labels and zoom_level > LOD_THRESHOLD:
                #label_cities(cities_map, city_names, int(config.CELL_SIZE * zoom_level))
            pygame.display.flip()
            render_update = False  # Reset update flag

        clock.tick(20)  # Maintain performance

if __name__ == "__main__":
    main()
