from ui_components.widgets.info_box import InfoBox
from ui_components.widgets.button import Button

class CollapsibleInfoBox(InfoBox):
    def __init__(self, large_font, small_font):
        super().__init__(large_font, small_font)
        self.toggle_button = Button(
            0, 0, 20, 20,
            action=self.toggle_expanded,
            toggle=False
        )

    def toggle_expanded(self):
        self.expanded = not self.expanded
        self.update_height()

    def draw(self, screen, x, y, parent_clip=None):
        super().draw(screen, x, y, parent_clip)
        self.toggle_button.rect.topleft = (x + self.width - self.toggle_button.rect.width - 4, y + 4)
        self.toggle_button.draw(screen)

    def handle_event(self, event):
        self.toggle_button.handle_event(event)
        self.title.handle_event(event)
        if self.info_box_list:
            self.info_box_list.handle_event(event)




