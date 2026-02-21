from together import Together
import json

client = Together()

model = "openai/gpt-oss-120b"

"""
A scenario with 7 interactions used 6000 input tokens and 1100 outputs tokens - about 0.2 of a cent. That is without history being inputted and outputted.  
"""

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

notebook_schema = {
    "type": "object",
    "properties": {
        "notebook_list": {
            "type": "array",
            "description": "list of key details about the user's character",
            "items": {"type": "string"}
        }
    },
    "required": ["notebook_list"],
    "additionalProperties": False
}

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
                        "enum": ["open-ended", "rating"]
                    },
                    "attribute_value": {
                        "type": "integer"
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
        max_tokens=500,
        reasoning_effort="low",
        messages=[
            {
                "role": "system",
                "content": f"""
                Convert the user's character description in to a list of characteristics and a list of attributes. 
                Attributes should be things that you expect to see in an RPG game and are relevant to the story focus and will change depending on the player's circumstances.
                Attributes should be in the form of an open-ended value or a rating /10.
                Attributes should be specific and measurable, not abstract things.
                The player should be given 4-8 attributes, and these will be used throughout the game to determine the player's progress.
                The list of characteristics will be used to decide on the player's actions in the story.
                Each characteristic is one short sentence fragment, and they should be concrete facts: role, personality traits, skills, equipment.
                Return ONLY valid JSON matching this schema: {character_setup_schema}.
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
                Update the character notebook if the given story changes any key details about the character.
                Only update elements in the notebook if significant changes in the character have occurred (new knowledge, equipment, experience, reputation).
                Return ONLY valid JSON matching this schema {notebook_schema}.
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
            "schema": notebook_schema
        }
    )
    print(response)
    data = json.loads(response.choices[0].message.content)
    return response.usage.completion_tokens, response.usage.prompt_tokens, data["notebook_list"]


def prompt_scenario(prompt, character_notebook):
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
                The player's skills and experiences are: {character_notebook}.
                With the context you have been provided, write a short interaction with the environment or situation that the character finds themselves in.
                Present the user with a variety of options on how to deal with the given interaction which represent different playstyles.
                Do not assume information about the world, use only the given context to generate interactions.
                Interaction descriptions should be no longer than 50 words, and each decision should be summarised in less than 15 words.
                Keep the tone and content of interactions consistent with the context provided.
                Each interaction should be focused on a single event/detail.
                Interactions should follow on previous interactions if provided, but MUST end after a few interactions. 
                If no previous interactions are given, assume the player has just entered the area.
                Any option that results in the player leaving, travelling on, retreating, camping, sleeping or resting should end the interaction by setting the exit_flag to True.
                Return ONLY valid JSON matching this schema: {scenario_schema}."""
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
