from storytelling.scene import Scene
import random

class SceneManager:
    def __init__(self, story_state, llm_client, context_builder):
        self.story_state = story_state
        self.llm_client = llm_client
        self.context_builder = context_builder

        self._pending_response_scene_guide = None
    
    def generate_scene_interaction(self, selected_cell):
        if self.story_state.current_scene:
            scene_history = self.story_state.current_scene.get_scene_history()
        else:
            scene_history = []
            self.story_state.current_scene = Scene()
        scene_guide = self.generate_scene_guide(self.context_builder.build_scene_guide_context(selected_cell), scene_history)

        # Store guide so poll() can use it when the stream finishes
        self._pending_response_scene_guide = scene_guide

        # Returns immediately — stream runs on a background thread
        self.llm_client.prompt_scene(
            scene_guide,
            self.story_state.current_scene.get_interactions(),
            self.story_state.world_description,
            self.story_state.story_focus_description
        )
    
    def generate_scene_guide(self, context, scene_history):
        significance_options = ["Very low", "Low", "Medium", "High"]
        scene_significance = significance_options[random.randint(0, len(significance_options) - 1)]
        response = self.llm_client.prompt_scene_setup(
            context,
            self.story_state.world_description,
            self.story_state.story_focus_description,
            self.story_state.character_description,
            scene_significance,
            self.story_state.notebook,
            scene_history
        )
        return response["guide"]
    
    def finalise_pending_interaction(self, response):
        """Called by StreamHandler once the stream output is finished."""
        self.story_state.current_scene.set_pending_interaction(
            response["description"],
            response["actions"],
            self._pending_response_scene_guide["outcome_suggestions"],
            self._pending_response_scene_guide
        )
        self._pending_response_scene_guide = None
        return response["prompt_tokens"], response["completion_tokens"]

    def end_scene(self, scene, selected_cell):
        response = self.llm_client.prompt_scene_summary(
            scene.get_interactions(),
            self.context_builder.get_chunk_context_json(selected_cell)
        )
        self.story_state.character_history.append(response["summary"])
        new_quest_list = []
        for quest in response["new_quests"]:
            print(f"Adding quest: {quest['chunk_id']} {quest['title']} {quest['visible_description']} {quest['hidden_description']}")
            new_quest_list.append({
                "chunk_id": quest["chunk_id"],
                "title": quest["title"],
                "visible_context": quest["visible_description"],
                "hidden_context": quest["hidden_description"]
                }
            )
        self.story_state.current_scene = None
        return new_quest_list, response["prompt_tokens"], response["completion_tokens"]
    
    def get_current_scene(self):
        return self.story_state.current_scene
 
    def clear_scene(self):
        self.story_state.current_scene = None
    
    def get_current_scene_debug_info(self):
        if self.story_state.current_scene:
            return {
                "focus": self.story_state.current_scene.focus,
                "environment": self.story_state.current_scene.environment,
                "significance": self.story_state.current_scene.significance
            }
        return None
    