import pygame
from utils import config

class EventHandler:
    def __init__(self):
        self.dragging = False
        self.drag_start_x, self.drag_start_y = 0, 0
        self.paused = False

    def handle_events(self, camera):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN):
                    self.handle_panning(event, camera)
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    self.dragging = True
                    self.drag_start_x, self.drag_start_y = pygame.mouse.get_pos()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                dx, dy = pygame.mouse.get_pos()
                camera.x_offset -= dx - self.drag_start_x
                camera.y_offset -= dy - self.drag_start_y
                self.drag_start_x, self.drag_start_y = dx, dy
            elif event.type == pygame.MOUSEWHEEL:
                camera.zoom(config.ZOOM_STEP * event.y, *pygame.mouse.get_pos())

    def handle_panning(self, event, camera):
        if event.key == pygame.K_LEFT:
            camera.x_offset -= config.PAN_STEP
        elif event.key == pygame.K_RIGHT:
            camera.x_offset += config.PAN_STEP
        elif event.key == pygame.K_UP:
            camera.y_offset -= config.PAN_STEP
        elif event.key == pygame.K_DOWN:
            camera.y_offset += config.PAN_STEP
