from storytelling.scene import Scene
import random

class SceneManager:
    def __init__(self, story_state, llm_client, context_builder):
        self.story_state = story_state
        self.llm_client = llm_client
        self.context_builder = context_builder
    
    async def generate_scene_interaction(self, selected_cell):
        if self.story_state.current_scene and not self.story_state.current_scene.ended:
            scene_history = self.story_state.current_scene.get_history()
        else:
            scene_history = []
            self.story_state.current_scene = Scene()
        
        scene_guide = await self.generate_scene_guide(
            self.context_builder.build_scene_guide_context(selected_cell), 
            scene_history
        )

        async for event in self.llm_client.prompt_interaction(
            scene_guide,
            self.story_state.current_scene.get_interactions(),
        ):
            yield event

        yield {"data": scene_guide, "event":"guide"}

    
    async def generate_scene_guide(self, context, scene_history):
        significance_options = ["Very low", "Low", "Medium", "High"]
        scene_significance = significance_options[random.randint(0, len(significance_options) - 1)]
        response = await self.llm_client.prompt_scene_setup(
            context,
            scene_significance,
            self.story_state.notebook,
            scene_history
        )
        return response["guide"]


    async def end_scene(self, scene, selected_cell):
        response = await self.llm_client.prompt_scene_summary(
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
        return new_quest_list
    
    def get_current_scene(self):
        return self.story_state.current_scene
 
    def clear_scene(self):
        self.story_state.current_scene = None
    

    