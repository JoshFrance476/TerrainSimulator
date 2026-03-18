import pygame
from app.commands import MouseDown, MouseMove, MouseUp, MouseWheel, KeyDown, KeyUp
import config

class InputSystem:
    def __init__(self, ui_manager):
        self.ui = ui_manager

    def build_commands(self, events):
        cmds = []

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = self.ui.get_clicked_component(event.pos)
                cmds.append(MouseDown(event.button, event.pos, clicked))

            elif event.type == pygame.MOUSEBUTTONUP:
                cmds.append(MouseUp(event.button))

            elif event.type == pygame.MOUSEMOTION:
                cmds.append(MouseMove(event.pos, pygame.mouse.get_pressed()[0]))

            elif event.type == pygame.MOUSEWHEEL:
                cmds.append(MouseWheel(event.y))

            elif event.type == pygame.KEYDOWN:
                cmds.append(KeyDown(event.key, event.unicode))
            
            elif event.type == pygame.KEYUP:
                cmds.append(KeyUp(event.key))

            elif event.type == pygame.QUIT:
                cmds.append(event)

        return cmds

    def continuous(self):
        keys = pygame.key.get_pressed()
        mouse_pos = pygame.mouse.get_pos()
        return keys, mouse_pos
