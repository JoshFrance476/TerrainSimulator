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
        "exit_flag": {"type": "boolean"},
        "options": {
            "type": "array",
            "description": "a list of 2-4 options that the user can choose",
            "items": {
                "type": "object",
                "properties": {
                    "action": {"type": "string"},
                },
                "required": ["action"],
                "additionalProperties": False
            }
        }
    },
    "required": ["interaction_description", "exit_flag", "options"],
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

def prompt_notebook_setup(character_desc):
    response = client.chat.completions.create(
        model=model,
        temperature=1,
        max_tokens=400,
        reasoning_effort="low",
        messages=[
            {
                "role": "system",
                "content": f"""
                Convert the user's character description in to a a list of characteristics. 
                These will be used to decide on the player's actions and experiences in the story.
                Each item is one short sentence fragment.
                Prefer concrete facts: role, personality traits, skills/experience, equipment.
                Return ONLY valid JSON matching this schema: {notebook_schema}.
                """
            },
            {
                "role": "user",
                "content": character_desc
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
                "content": f"""You are the storyteller in a single-player game set on a 2D map made up of tiles.
                The game is focused on realism and immersion in a given world. Situations should be natural and believable.
                The user moves their character around the map, and can trigger interactions to get a description of their surroundings and possible choices.
                The user has defined the world context, their character and the type of stories they want to experience.
                The player's skills and experiences are: {character_notebook}.
                You will be prompted to generate interactions or end scenarios based on given context, which should reflect the environment the character finds themselves in.
                Do not assume information about the world, use only the given context to generate interactions.
                Interaction descriptions should be no longer than 50 words, and each decision should be summarised in less than 15 words.
                Keep the tone and content of interactions consistent with the context provided.
                Each interaction should be focused on a single event/detail.
                If no previous interactions are given, assume the player has just entered the area.
                Any option that results in the player leaving, travelling on, retreating, camping, sleeping, resting counts as an exit option.
                Exit options must not carry on the interaction, they end it.
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
        data["exit_flag"],
        data["options"],
    )
