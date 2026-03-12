from storytelling.llm_prompting import new_region_schema, scene_schema, story_setup_schema, summary_schema, character_setup_schema, scene_setup_schema
from together import Together
import json



class StoryLLM:
    def __init__(self):
        self.client = Together()
        self.model = "openai/gpt-oss-120b"

        self.new_region_schema = new_region_schema
        self.scene_schema = scene_schema
        self.story_setup_schema = story_setup_schema
        self.summary_schema = summary_schema
        self.character_setup_schema = character_setup_schema
    
    def prompt_scene(self, context, world_desc, story_focus_desc):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=600,
            reasoning_effort="low",
            messages=[
                {
                    "role": "system",
                    "content": f"""You are the storyteller in a single-player game set on a procedurally-generated map.
                    The game is focused on realism and immersion in a given world. Situations should be natural and believable.
                    The world is made up of tiles representing a small area of the map. Each interaction takes place on one tile and shouldn't involve moving to other tiles.
                    The user has defined the world context, their character and the type of stories they want to experience.
                    Based on the given context, write a short second-person description of the player's situation.
                    Provide the player with several actions that they can perform, with a probability of success (as a percentage) based on the character and the situation.
                    Actions should be directly related to the description you provide and the character's abilities.
                    Most actions should have a probability of 100, only give 'challenging' actions a non-certain probability.
                    You will receive a single JSON object in the user message under CONTEXT_JSON.
                    The context you will be provided with:
                    Tile interaction history: Will show the previous descriptions and player actions. Provided in chronological order.
                    Latest tile action: Follow on from this.
                    Character notebook: Provides key details on the character. Base actions on this.
                    The scene_prompt is only the initial premise of the scene.
                    If tile interaction history is not null, do not restate or restart the scene_prompt unless the latest action directly causes attention to return to it.
                    If tile interaction history is null, introduce the scene using scene_prompt and scene_environment.
                    Each interaction should meaningfully progress the scene.
                    Scene environment: Use this to immerse the player in the world.
                    Interaction descriptions should be no longer than 50 words, and each action summarised in less than 15 words.
                    The player can read their previous interactions, so don't repeat details if it's not necessary.
                    Any option that results in the player leaving, travelling on, sleeping or resting should end the interaction by setting the exit_flag to True.
                    Unless the current situation is unavoidable, the player should be provided an option to continue travelling with exit_flag. This option should be a vague "carry on moving" and not a "travel to (location)"
                    Description of the world: {world_desc}. Description of the story focus: {story_focus_desc}.
                    Return only JSON matching the provided schema."""
                },
                {
                    "role": "user",
                    "content": context
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "scene",
                    "schema": scene_schema
                }
            }
        )
        data = json.loads(response.choices[0].message.content)
        print(response)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "description": data["interaction_description"],
            "actions": data["actions"]
        }
    
    def prompt_story_setup(self, character_desc, world_desc, story_focus_desc):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            max_tokens=2000,
            reasoning_effort="medium",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You are setting up a list of potential scenes to give to a storyteller in a single-player game set on a procedurally-generated map.
                    This list of scenes will be used to inspire quests and situations that the player will find themselves in and make decisions about.
                    The game is focused on realism and immersion in a given world. Scenes should be natural and believable within the given context.
                    Given the context that the user has provided, generate a list of 8-14 different scenes that the user might experience in the world.
                    Each scene should be one sentence describing a location or a situation that the player might find themselves in.
                    Scenes should be immersive and unpredictable to create an exciting role-playing story game where the players decisions have an impact on their experience.
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    Character description: {character_desc},
                    World description: {world_desc},
                    Story focus: {story_focus_desc}.
                    """
                }
            ],
            response_format={
                "type": "json_schema",
                "schema": story_setup_schema
            }
        )
        data = json.loads(response.choices[0].message.content)
        print(response)
        return {
            "completion_tokens": response.usage.completion_tokens, 
            "prompt_tokens": response.usage.prompt_tokens, 
            "story_list": data["story_list"]}

    def prompt_scene_summary(self, scene, chunk_list):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=400,
            reasoning_effort="low",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You summarise interactions that the player has in a singleplayer procedural story game.
                    The world is dynamic and reacts to the players decisions.
                    You will be given a short section of story which involves actions that the player has performed.
                    Produce a short summary of what the player has gained from the interaction.
                    You will also be provided with a list of features around the player.
                    If the player has learned about landmark or point-of-interest that they are not currently at, produce a 'region' schema to add the region to the world.
                    The feature_id will be used to add the region to the relevant feature on the map.
                    The region should describe what the player will find at the location, and will be used to generate a narrative when the player arrives there.

                    Summary must be succinct:
                    - 5-15 words only
                    - Describe specifically what the character gained from the interaction
                    - Should describe where the action took place
                    """
                },
                {
                    "role": "user",
                    "content": f"{scene}. Feature List: {chunk_list}"
                }
            ],
            tools=[{"type": "function", "function": new_region_schema},
                {"type": "function", "function": summary_schema}],
        )
        summary = None
        new_region = None

        print(response)

        for tool_call in response.choices[0].message.tool_calls:
            args = json.loads(tool_call.function.arguments)

            if tool_call.function.name == "generate_summary":
                summary = args.get("summary")
            elif tool_call.function.name == "create_region":
                new_region = {
                    "feature_id": args.get("feature_id"),
                    "title": args.get("title"),
                    "visible_description": args.get("visible_description"),
                    "hidden_description": args.get("hidden_description")
                }
            
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "summary": summary,
            "new_region": new_region
        }

    def prompt_scene_setup(self, context, world_desc, story_focus_desc, character_desc, significance):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=800,
            reasoning_effort="medium",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    You generate scene setup prompts for a single-player procedural storytelling game.

                    Your task is to produce a short scene setup that will later be expanded by another LLM storyteller.

                    The game prioritizes realism, immersion, and believable situations within the world.

                    OUTPUT REQUIREMENTS

                    Return ONLY valid JSON matching the provided schema.

                    The JSON must contain:

                    1. scene_prompt
                    - Exactly ONE sentence.
                    - Describes the situation the player finds themselves in.
                    - Should be engaging, realistic, and slightly unpredictable.
                    - Should suggest a situation where the player may need to make a decision.

                    2. environment_description
                    - Exactly ONE sentence.
                    - Describes the immediate environment or location.
                    - Must be based ONLY on the provided context.
                    - Do NOT invent new environmental features.
                    - If the location has little detail, acknowledge the lack of notable features rather than inventing them.

                    SCENE DESIGN RULES

                    - Scenes should feel natural within the world.
                    - Avoid dramatic or unrealistic events unless strongly supported by the context.
                    - The situation should feel like something the player has just encountered.
                    - Keep descriptions concise and grounded.
                    - Do not narrate outcomes or player actions.

                    You will also receive a "significance" level indicating how impactful the situation should be:
                    - low: minor or atmospheric moment
                    - medium: interesting situation with potential interaction
                    - high: important or tense moment affecting the story
                    
                    CONTEXT:

                    World description: {world_desc}.
                    Story focus: {story_focus_desc}.
                    Character description: {character_desc}.
                    Return only JSON matching the provided schema.
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    Location context: {context}.
                    Significance: {significance}.
                """
                }
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "scene_setup",
                    "schema": scene_setup_schema
                }
            }
        )
        data = json.loads(response.choices[0].message.content)
        print(response)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "focus": data["scene_prompt"],
            "environment": data["environment_description"]
            }
    
    def prompt_character_setup(self, character_desc, world_desc, story_focus_desc):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            max_tokens=800,
            reasoning_effort="low",
            messages=[
                {
                    "role": "system",
                    "content": f"""
                    Convert the user's character description into:
                    - notebook_list: concrete character characteristics (facts)
                    - attribute_list: 4-8 RPG-style attributes that are measurable and can change during play

                    Definitions:
                    A) notebook_list (characteristics)
                    - Each entry is a short sentence fragment (3-12 words).
                    - Must be key points that describe the character.
                    - equipment/resources
                    - skill/training
                    - Injury/condition
                    - Personality/characteristics
                    - No numbers, no ratings, no vague abstractions.

                    B) attribute_list (attributes)
                    - 4-8 total.
                    - Must be relevant to the story focus and expected to change with circumstances.
                    - Must be specific and measurable (not abstract like “destiny”, “hope”, “goodness”).
                    - Avoid duplicates/overlap (e.g., don't include both “Strength” and “Power”).
                    - Use standard RPG-like stats + survival/story-relevant meters (e.g., Health, Stamina, Hunger, Thirst, Morale, Engineering, Combat, Navigation).

                    Attribute formats (MUST follow):
                    - If attribute_type == "rating": attribute_value is an integer 0-10.
                    - If attribute_type == "category": attribute_value is one of:
                    "very low", "low", "medium", "high", "very high"
                    - If attribute_type == "open-ended": attribute_value is any integer

                    Initial values:
                    - Ratings should be plausible and grounded in the description (avoid all 10s).
                    - Category values should be conservative if uncertain.

                    Output rules:
                    - Return ONLY valid JSON matching this schema: {json.dumps(character_setup_schema)}
                    - Do not include any extra keys (no summary, no explanations).
                    """
                },
                {
                    "role": "user",
                    "content": f"""
                    Character description: {character_desc},
                    World description: {world_desc},
                    "Story focus: {story_focus_desc}.
                    """
                }
            ],
            response_format={
                "type": "json_schema",
                "schema": character_setup_schema
            }
        )
        print(response)
        data = json.loads(response.choices[0].message.content)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "notebook": data["notebook_list"],
            "attributes": data["attribute_list"]
            }