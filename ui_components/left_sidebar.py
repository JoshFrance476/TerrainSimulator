import pygame
import config
from ui_components.widgets.info_box_list import InfoBoxList

class LeftSidebarController:
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.info_box_list = InfoBoxList(config.SIDEBAR_WIDTH - 20, config.SCREEN_HEIGHT-60)


    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        title_text = self.fonts.large_font.render(self.title, True, (30,30,30))
        screen.blit(title_text, (10, 20))

        if self.info_box_list:
            self.info_box_list.draw(screen, 10, 50)



