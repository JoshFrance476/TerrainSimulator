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
        "notebook_list": {
            "type": "array",
            "description": "list of key details about the user's character",
            "items": {"type": "string"}
        },
        "summary": {
            "type": "string",
            "description": "Very short summary of the character's experience to add to character history"
        }
    },
    "required": ["notebook_list", "summary"],
    "additionalProperties": False
}

def prompt_scenario_summary(scenario, notebook):
    response = client.chat.completions.create(
        model=model,
        temperature=1,
        max_tokens=400,
        reasoning_effort="low",
        messages=[
            {
                "role": "system",
                "content": f"""
                You summarise logs of events that the user's character experiences.
                You will be given a short section of story which involves actions that the user's character has performed.
                CRITICAL RULES (must follow):
                1) Notebook updates are RARE. Do NOT add or modify notebook items unless the story causes a durable change in the character:
                - New or lost equipment/resources that persist
                - New learned skill/training gained
                - Injury/condition that persists
                - Major reputation/faction relationship change
                - Major objective/role change
                If none of the above occurred, return the notebook_list EXACTLY as provided, with no additions, removals, or edits.

                2) Summary must be succinct:
                - 4-12 words only
                - Give an overview of what the character experienced (a past-tense verb phrase)
                - Minimal setting details and context
                Return ONLY valid JSON matching this schema {json.dumps(summary_schema)}.
                Provided is the current notebook: {notebook}.
                """
            },
            {
                "role": "user",
                "content": scenario
            }
        ],
        response_format={
            "type": "json_schema",
            "schema": summary_schema
        }
    )
    print(response)
    data = json.loads(response.choices[0].message.content)
    return response.usage.completion_tokens, response.usage.prompt_tokens, data["notebook_list"], data["summary"]




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

def prompt_scenario(prompt):
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
                The user has defined the world context, their character and the type of stories they want to experience.
                With the context you have been provided and the previous actions the player has taken, write a short description of the environment or situation that the character finds themselves in,  following on from the story history.
                The description should be in the second-person, telling the player what their character is experiencing.
                Provide the player with several actions that they can perform based on the character's traits, with a probability of success (as a percentage) based on the character and the situation.
                Actions should be directly related to the description you provide.
                Most actions should have a probability of 100, only give 'challenging' actions a non-certain probability.
                You will receive a single JSON object in the user message under CONTEXT_JSON.
                Treat fields as follows:
                - world.description, story.focus, character.notebook, character.history, tile, recent_events are authoritative.
                - Never contradict character.notebook facts.
                - Use character.history/recent_events only for continuity; do not invent new named world facts.
                - You may infer mundane, non-contradictory sensory details from tile (biome/weather/time), but must not invent named factions/landmarks/history unless present in the JSON.

                Interaction descriptions should be no longer than 50 words, and each decision should be summarised in less than 15 words.
                Keep the tone and content of interactions consistent with the context provided.
                Interactions should follow on previous interactions if provided, but MUST end after a few interactions. 
                If no previous interactions are given, assume the player has just entered the area.
                If the most recent player action is provided, the description should focus on the consequences of that action.
                Don't repeat what has already been described to the player.
                You should assume that the context describes a small area around the character, and actions must not move the player from that area.
                Any option that results in the player leaving, travelling on, sleeping or resting should end the interaction by setting the exit_flag to True.
                Return ONLY valid JSON matching this schema: {json.dumps(scenario_schema)}."""
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
