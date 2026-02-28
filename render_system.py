class RenderSystem:
    def __init__(self, ui_manager, map_renderer, fps_monitor):
        self.ui = ui_manager
        self.map_renderer = map_renderer
        self.fps = fps_monitor
    
    def render(self, screen):
        self.map_renderer.render_view(screen)
        self.fps.tick()
        self.ui.draw_fps_counter(screen, self.fps.get_fps())
        self.ui.render_ui(screen)