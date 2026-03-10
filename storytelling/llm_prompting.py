from together import Together
import json

client = Together()

model = "openai/gpt-oss-120b"

"""
A scenario with 7 interactions used 6000 input tokens and 1100 outputs tokens - about 0.2 of a cent. That is without history being inputted and outputted.  
"""
story_setup_schema = {
    "type": "object",
    "properties": {
        "scenario_list": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

def prompt_story_setup(character_desc, world_desc, story_focus_desc):
    response = client.chat.completions.create(
        model=model,
        temperature=1,
        max_tokens=800,
        reasoning_effort="medium",
        messages=[
            {
                "role": "system",
                "content": f"""
                You are setting up a list of possible scenarios for a singleplayer story game.
                Given the context that the user has provided, generate a list of 8-14 different scenario prompts that the user might experience in the world.
                Scenarios should be short and ambiguous.
                Return ONLY valid JSON matching this schema: {json.dumps(story_setup_schema)}
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
            "schema": story_setup_schema
        }
    )
    print(response)
    data = json.loads(response.choices[0].message.content)
    return response.usage.completion_tokens, response.usage.prompt_tokens, data["scenario_list"]


character_setup_schema = {
    "type": "object",
    "properties": {
        "notebook_list": {
            "type": "array",
            "description": "list of key details about the user's character",
            "items": {"type": "string"}
        },
        "attribute_list": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "attribute": {
                        "type": "string"
                    },
                    "attribute_type": {
                        "type": "string",
                        "enum": ["open-ended", "rating","category"]
                    },
                    "attribute_value": {
                        "oneOf": [
                            {
                                "type": "integer"
                            },
                            {
                                "type": "string",
                                "enum": ["very low", "low", "medium", "high", "very high"]
                            }
                        ]
                    }
                },
                "required": ["attribute", "attribute_type", "attribute_value"],
                "additionalProperties": False
            }
        }
    },
    "required": ["notebook_list", "attribute_list"],
    "additionalProperties": False
}

def prompt_character_setup(character_desc, world_desc, story_focus_desc):
    response = client.chat.completions.create(
        model=model,
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
    return response.usage.completion_tokens, response.usage.prompt_tokens, data["notebook_list"], data["attribute_list"]




summary_schema = {
    "type": "object",
    "properties": {
        "new_region":
        {
            "type": "object",
            "properties": {
                "feature_id": {
                    "type": "integer"
                },
                "title": {
                    "type": "string",
                    "description": "1-4 words"
                },
                "visible_description": {
                    "type": "string",
                    "description": "Describe what the player expects to find at the location"
                },
                "hidden_description": {
                    "type": "string",
                    "description": "Explicit hidden lore and story prompts that the player will discover by investigating the location"
                }
            }
        },
        "summary": {
            "type": "string",
            "description": "Very short summary of the character's experience"
        }
    },
    "required": ["new_region", "summary"],
    "additionalProperties": False
}

def prompt_scenario_summary(scenario, chunk_list):
    response = client.chat.completions.create(
        model=model,
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
                If the player has learned about something in the area, produce a 'region' schema to add the region to the world.
                The feature_id will be used to add the region to the relevant feature on the map.
                The region should describe what the player will find at the location, and will be used to generate a narrative when the player arrives there.

                Summary must be succinct:
                - 5-15 words only
                - Describe specifically what the character gained from the interaction
                - Should describe where the action took place

                
                Return ONLY valid JSON matching this schema {json.dumps(summary_schema)}.
                """
            },
            {
                "role": "user",
                "content": f"{scenario}. Feature List: {chunk_list}"
            }
        ],
        response_format={
            "type": "json_schema",
            "schema": summary_schema
        }
    )
    print(response)
    data = json.loads(response.choices[0].message.content)
    return response.usage.completion_tokens, response.usage.prompt_tokens, data["summary"], data['new_region']




scenario_schema = {
    "type": "object",
    "properties": {
        "interaction_description": {"type": "string"},
        "options": {
            "type": "array",
            "description": "a list of 2-4 options that the user can choose",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                    "exit_flag": {"type": "boolean"},
                    "probability": {"type": "integer"}
                },
                "required": ["action", "exit_flag"],
                "additionalProperties": False
            }
        }
    },
    "required": ["interaction_description", "options"],
    "additionalProperties": False
}

def prompt_scenario(prompt, world_desc, story_focus_desc):
    response = client.chat.completions.create(
        model=model,
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
                Based on the previous actions the player has taken, write a short description of the player's situation.
                The description should be in the second-person.
                Provide the player with several actions that they can perform, with a probability of success (as a percentage) based on the character and the situation.
                Actions should be directly related to the description you provide and the character's abilities.
                Most actions should have a probability of 100, only give 'challenging' actions a non-certain probability.
                You will receive a single JSON object in the user message under CONTEXT_JSON.
                The context you will be provided with:
                Character notebook: Provides key details on the character. Base actions on this.
                Previous actions on other tiles: This is what the player has already experienced elsewhere on the map. Use it to provide continuity and build on it.
                Movement: Describes the tile the player was previously on, which direction they moved, and the tile they are on now. Use it to frame the situation.
                Tile: Describes the current tile the player is on.
                Biome: Self explanatory
                Details: Provides a list of all relevant story context.
                Visible description: This is context that is known to the player. Treat this as fact.
                Hidden description: This is context that is hidden from the player. Use it to build exciting and engaging narratives.
                Previous events on this tile: If the player has already begun their interaction on the current tile, this will show the previous descriptions and player actions. These are provided in chronological order, you should follow on from the last one.
                Location context: This describes the tiles around the player and their direction. Use it to immerse the player.
                Interaction descriptions should be no longer than 50 words, and each action should be summarised in less than 15 words.
                Interactions should follow on previous interactions if provided, but MUST end after a few interactions. 
                The player can read their previous interactions, so don't repeat details if it's not necessary.
                Any option that results in the player leaving, travelling on, sleeping or resting should end the interaction by setting the exit_flag to True.
                Unless the current situation is unavoidable, the player should be provided an option to continue travelling with exit_flag. This option should be a vague "carry on moving" and not a "travel to (location)"
                Return ONLY valid JSON matching this schema: {json.dumps(scenario_schema)}.
                Description of the world: {world_desc}. Description of the story focus: {story_focus_desc}."""
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        response_format={
            "type": "json_schema",
            "schema": scenario_schema
        }
    )
    print(response)
    data = json.loads(response.choices[0].message.content)
    return (
        response.usage.completion_tokens,
        response.usage.prompt_tokens,
        data["interaction_description"],
        data["options"],
    )
