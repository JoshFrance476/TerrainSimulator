from backend.storytelling.interaction import Interaction

class Scene:
    def __init__(self):
        self.completed_interactions = []
        self.pending_interaction = None
        self.ended = False
        self.interaction_count = 0
    
    def end_scene(self):
        self.ended = True
    
    def get_interactions(self):
        interactions = []
        for interaction in self.completed_interactions:
            interactions.append({"Situation": interaction.description,
                                 "Action": interaction.chosen_action})
        return interactions

    def set_pending_interaction(self, description, actions, outcomes, guide):
        self.pending_interaction = Interaction(description, actions, outcomes, guide)
    
    def submit_action(self, action):
        self.pending_interaction.set_chosen_action(action)
        if self.pending_interaction.ends_scene():
            self.end_scene()
        self.completed_interactions.append(self.pending_interaction)
        self.interaction_count += 1
        self.pending_interaction = None

    def get_outcomes(self):
        outcome_list = []
        for interaction in self.completed_interactions:
            outcome_list.append(interaction.outcome)
        return outcome_list[::-1]
    
    def get_scene_history(self):
        return {
            f"scene_{idx}": {
                "environment_description": interaction.guide["environment_description"],
                "precise_location": interaction.guide["precise_location"],
                "story": interaction.guide["story_suggestion"],
                "action": interaction.outcome
            }
            for idx, interaction in enumerate(self.completed_interactions)
        }
    