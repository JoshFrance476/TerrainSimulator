from together import Together
import json

client = Together()

model = "openai/gpt-oss-120b"

"""
A scenario with 7 interactions used 6000 input tokens and 1100 outputs tokens - about 0.2 of a cent. That is without history being inputted and outputted.  
"""

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
        reasoning_effort="medium",
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

                2) Summary must be ultra-succinct:
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
                    "exit_flag": {"type": "boolean"}
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
        temperature=1,
        max_tokens=400,
        reasoning_effort="low",
        messages=[
            {
                "role": "system",
                "content": f"""You are the storyteller in a single-player game set on a procedurally-generated map.
                The game is focused on realism and immersion in a given world. Situations should be natural and believable.
                The user has defined the world context, their character and the type of stories they want to experience.
                With the context you have been provided, write a short interaction with the environment or situation that the character finds themselves in.
                Present the user with a variety of options on how to deal with the given interaction which represent different playstyles.
                Do not assume information about the world, use only the given context to generate interactions.
                Interaction descriptions should be no longer than 50 words, and each decision should be summarised in less than 15 words.
                Keep the tone and content of interactions consistent with the context provided.
                Each interaction should be focused on a single event/detail.
                Interactions should follow on previous interactions if provided, but MUST end after a few interactions. 
                If no previous interactions are given, assume the player has just entered the area.
                Any option that results in the player leaving, travelling on, retreating, camping, sleeping or resting should end the interaction by setting the exit_flag to True.
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
