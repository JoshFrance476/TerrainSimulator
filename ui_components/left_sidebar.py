import pygame
import config
from ui_components.widgets.collapsible_info_box import CollapsibleInfoBox
from ui_components.widgets.info_box_list import InfoBoxList
from functools import partial

class LeftSidebarController:
    def __init__(self, fonts, controller):
        self.fonts = fonts
        self.controller = controller
        self.title = ""
        self.info_box_list = InfoBoxList(config.SIDEBAR_WIDTH - 20, config.SCREEN_HEIGHT-60)

        self.state_info_boxes = {}
        self.settlement_info_boxes = {}
        self.event_info_boxes = {}
        self.storyline_info_boxes = {}

        self.storyline_state = {
            "storylines":{},
            "scroll_offset":0
        }


    def show_settlements(self, settlements_dict):
        self.title = "Settlements"
        self.info_box_list.reset()
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
        self.info_box_list.reset()
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
        self.info_box_list.reset()
        for event in event_log:
            if event.tick_count not in self.event_info_boxes:
                box = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.event_info_boxes[event.tick_count] = box
            else:
                box = self.event_info_boxes[event.tick_count]

            box.set_info(event.description, {"Tick": str(event.tick_count)}, {"Location": f"{event.location[0]}, {event.location[1]}", "Narrative": event.narrative})
            self.info_box_list.add_info_box(box)
    
    

    def show_storylines(self, storyline_list):
        self.title = "Storylines"
        self.info_box_list.reset()

        # Ensure keys exist
        if "storylines" not in self.storyline_state:
            self.storyline_state["storylines"] = {}

        for storyline in storyline_list:
            storyline_id = id(storyline)

            # Reuse existing CollapsibleInfoBox if available
            if storyline_id not in self.storyline_info_boxes:
                storyline_obj = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                self.storyline_info_boxes[storyline_id] = storyline_obj
            else:
                storyline_obj = self.storyline_info_boxes[storyline_id]

            # Restore state
            state = self.storyline_state["storylines"].get(storyline_id, {})
            storyline_obj.expanded = state.get("expanded", False)
            storyline_obj.set_info(storyline.overview, {}, {"Scope": storyline.scope})

            # Ensure nested InfoBoxList exists
            if storyline_obj.info_box_list is None:
                storyline_obj.info_box_list = InfoBoxList(self.info_box_list.width - 10, 200)

            storyline_obj.info_box_list.scroll_offset = state.get("scroll_offset", 0)

            # Build or update child event boxes
            existing_events = {
                getattr(box, "event_id", None): box
                for box in storyline_obj.info_box_list.info_boxes
            }
            storyline_obj.info_box_list.info_boxes.clear()

            for event in storyline.events:
                event_id = id(event)
                if event_id not in existing_events:
                    event_obj = CollapsibleInfoBox(self.fonts.large_font, self.fonts.small_font)
                    event_obj.event_id = event_id
                else:
                    event_obj = existing_events[event_id]

                event_obj.set_info(
                    event.description,
                    {"Tick": str(event.tick_count)},
                    {"Location": f"{event.location[0]}, {event.location[1]}", "Narrative": event.narrative},
                )

                # Restore expanded toggle
                event_state = state.get("events", {}).get(event_id, {})
                if event_state.get("expanded", False):
                    event_obj.toggle_expanded()

                storyline_obj.info_box_list.add_info_box(event_obj)

            self.info_box_list.add_info_box(storyline_obj)


    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (0, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        title_text = self.fonts.large_font.render(self.title, True, (30,30,30))
        screen.blit(title_text, (10, 20))

        if self.info_box_list:
            self.info_box_list.draw(screen, 10, 50)

    def handle_event(self, event):
        if self.info_box_list:
            self.info_box_list.handle_event(event)
        
        self.storyline_state["scroll_offset"] = self.info_box_list.scroll_offset
        for storyline_id, storyline_obj in self.storyline_info_boxes.items():
            if storyline_id not in self.storyline_state["storylines"]:
                self.storyline_state["storylines"][storyline_id] ={}
            
            self.storyline_state["storylines"][storyline_id].update({
                "expanded": storyline_obj.expanded,
                "scroll_offset": storyline_obj.info_box_list.scroll_offset,
                "events": {
                    id(event_obj): {"expanded": event_obj.expanded}
                    for event_obj in getattr(storyline_obj.info_box_list, "info_boxes", [])
                },
            })



