import pygame
import config
from ui_components.widgets.label import Label
from ui_components.widgets.line_divider import LineDivider
from ui_components.widgets.button import Button
from ui_components.widgets.container_list import ContainerList
from ui_components.widgets.component_container import ComponentContainer
from ui_components.widgets.textbox import TextBox


class RightSidebarController:
    def __init__(self, fonts, storyteller, interaction_system, biome_config):
        self.fonts = fonts
        self.component_list = []
        self.biome_config = biome_config

        self.interaction_system = interaction_system
        self.storyteller = storyteller

    def show_current_scenario_screen(self):
        self.clear_page()
        self.component_list.append(Label("Current Scenario", self.fonts.header, config.SIDEBAR_WIDTH))

        interaction_list = ContainerList(config.SIDEBAR_WIDTH-10, 500, True)
        current_scenario = self.storyteller.get_current_scenario()
        if current_scenario:
            for completed_interactions in current_scenario.completed_interactions:
                interaction_container = ComponentContainer()
                interaction_container.add_component(Label(completed_interactions.description, self.fonts.small_font, config.SIDEBAR_WIDTH-20))
                interaction_container.add_component(Label(completed_interactions.decision, self.fonts.small_font, config.SIDEBAR_WIDTH-20))
                interaction_list.add_container(interaction_container)

            pending_interaction = current_scenario.pending_interaction
            interaction_container = ComponentContainer()
            if pending_interaction:
                interaction_container.add_component(Label(pending_interaction.description, self.fonts.small_font, config.SIDEBAR_WIDTH-20))
                for index, action in enumerate(pending_interaction.actions):
                    interaction_container.add_component(Button(200, 50, lambda i = index: self.interaction_system.submit_pending_interaction_action(i), (action['action'] + str(action["probability"])), self.fonts.small_font))
                custom_action_textbox = TextBox(self.interaction_system, self.fonts.small_font, 200, 20)
                interaction_container.add_component(custom_action_textbox)
                interaction_container.add_component(Button(50,20, lambda: self.interaction_system.submit_custom_pending_interaction_action(custom_action_textbox.text), "Submit", self.fonts.small_font))
            else:
                interaction_container.add_component(Button(200, 30, lambda: self.interaction_system.exit_scenario(), "Exit scenario", self.fonts.small_font))
            interaction_list.add_container(interaction_container)
        else:
            scenario_prompt_button = Button(60,20, lambda: self.interaction_system.prompt_scenario(), "Prompt", self.fonts.small_font)
            self.component_list.append(scenario_prompt_button)
        self.component_list.append(interaction_list) 

    def clear_page(self):
        self.component_list = []
    
        
    def draw(self, screen):
        pygame.draw.rect(screen, (220,220,220),
                         (config.SCREEN_WIDTH, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT))
        pygame.draw.rect(screen, (80,80,80),
                         (config.SCREEN_WIDTH, 0, config.SIDEBAR_WIDTH, config.SCREEN_HEIGHT), 3)

        y_offset = 10
        for component in self.component_list:
            if isinstance(component, list):
                x_offset = config.SCREEN_WIDTH
                for subcomponent in component:
                    subcomponent.draw(screen, subcomponent.left_padding+x_offset, y_offset)
                    x_offset += subcomponent.width
                y_offset += component[0].height
            else:
                if hasattr(component, "top_padding"):
                    y_offset += component.top_padding
                component.draw(screen, config.SCREEN_WIDTH+component.left_padding, y_offset)
                y_offset += component.height
