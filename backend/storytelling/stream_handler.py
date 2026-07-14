class StreamHandler:
    def __init__(self, state, scene_manager):
        self.state = state
        self.scene_manager = scene_manager
 
    def poll(self):
        """Called every frame by the main loop (through story engine). Drains chunk_queue and finalises
        the interaction once the stream terminator arrives. Returns True if UI needs a refresh."""
        if self.state.chunk_queue.empty():
            return False

        item = self.state.chunk_queue.get_nowait()

        if isinstance(item, tuple) and item[0] == "__done__":
            response = item[1]
            self.scene_manager.finalise_pending_interaction(response)
            self.state.stream_response = ""
            return True

        if isinstance(item, tuple) and item[0] == "__error__":
            print(f"[StreamHandler] LLM error: {item[1]}")
            return True

        self.state.stream_response += item
        return True