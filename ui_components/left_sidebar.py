import pygame
import config
from ui_components.widgets import InfoBoxList, CollapsibleInfoBox
from functools import partial

class LeftSidebarController:
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.info_box_list = None

        self.state_info_boxes = {}
        self.settlement_info_boxes = {}
        self.event_info_boxes = {}

    def show_settlements(self, settlements_dict):
        self.title = "Settlements"
        self.info_box_list = InfoBoxList(10, 50, config.SIDEBAR_WIDTH - 20)
        for s in settlements_dict.values():
            if s.id not in self.settlement_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.settlement_info_boxes[s.id] = box
            else:
                box = self.settlement_info_boxes[s.id]

            box.set_info(s.name, {"Location": f"{s.r}, {s.c}"}, {"Population": f"{s.population:.2f}"})
            box.add_text_link_action(partial(self.controller.select_settlement, s.r, s.c))
            self.info_box_list.add_info_box(box)

    def show_states(self, states_dict):
        self.title = "States"
        self.info_box_list = InfoBoxList(10, 50, config.SIDEBAR_WIDTH - 20)
        for s in states_dict.values():
            if s.id not in self.state_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.state_info_boxes[s.id] = box
            else:
                box = self.state_info_boxes[s.id]

            box.set_info(str(s.name), {"Tile Capacity": f"{s.tile_capacity:.0f}"}, {"Tile Count": s.tile_count})
            box.add_text_link_action(partial(self.controller.select_state, s.id))
            self.info_box_list.add_info_box(box)
    
    def show_event_log(self, event_log):
        self.title = "Event Log"
        self.info_box_list = InfoBoxList(10, 50, config.SIDEBAR_WIDTH - 20)
        for event in event_log:
            if event["tick_count"] not in self.event_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.event_info_boxes[event["tick_count"]] = box
            else:
                box = self.event_info_boxes[event["tick_count"]]

            box.set_info(event['event_type'].title(), {"Tick": str(event['tick_count'])}, {"Location": f"{event['location'][0]}, {event['location'][1]}", "Description": event['event_desc']})
            self.info_box_list.add_info_box(box)

    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        title_text = self.fonts.large_font.render(self.title, True, (30,30,30))
        screen.blit(title_text, (10, 20))

        if self.info_box_list:
            self.info_box_list.draw(screen)

    def handle_event(self, event):
        if self.info_box_list:
            self.info_box_list.handle_event(event)



