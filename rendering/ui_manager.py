import pygame
from utils import config

class UIManager:
    def __init__(self):
        self.font = pygame.font.Font("fonts/VCR_OSD_MONO_1.001.ttf", config.FONT_SIZE)

    def draw_sidebar(self, screen, selected_cell, terrain_data):
        sidebar_x = config.WIDTH
        pygame.draw.rect(screen, (220, 220, 220), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.HEIGHT))
        pygame.draw.rect(screen, (80, 80, 80), (sidebar_x, 0, config.SIDEBAR_WIDTH, config.HEIGHT), 3)
        
        text = self.font.render(f"Cell: {selected_cell}", True, (30, 30, 30))
        screen.blit(text, (sidebar_x + 10, 20))
