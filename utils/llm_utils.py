from openai import OpenAI
import json

client = OpenAI()

model = "gpt-5-mini"

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
            }}
    },
    "required": ["interaction_description", "exit_flag", "options"],
    "additionalProperties": False
    }
    



def prompt_scenario(prompt):
    response = client.responses.parse(
        model=model,
        instructions= """You are the storyteller in a single-player game set on a 2D map made up of tiles.
            The game is focused on realism and immersion in a given world. Situations should be natural and believable.
            The user moves their character around the map, and can trigger interactions to get a description of their surroundings and possible choices.
            The user has defined the world context, their character and the type of stories they want to experience.
            You will be prompted to generate interactions based on given context, which should reflect the environment the character finds themselves in.
            Do not assume information about the world, use only the given context to generate interactions.
            Interaction descriptions should be no longer than 50 words, and each decision should be summarised in less than 15 words.
            Keep the tone and content of interactions consistent with the background that the user has provided.
            Interactions should not involve travelling, as they occur within a singular tile in the world.
            Each interaction should be focused on a single event/detail and should progress the story.
            If no previous interactions are given, you should assume the player has just entered the area. If previous interactions are given, the next interaction should follow on from the most recent one.
            Scenarios should highlights a certain situation or decision in the given location, and should end when the player leaves the area.
            Unless the current situation is unavoidable, the player should be provided an option leave the area.
            To end scenarios, set the 'exit_flag' flag to True and return options as an empty list.
            """,
        input=prompt,
        temperature=1,
        stream=False,
        text={
            "format": {
                "type": "json_schema",
                "name": "interaction",
                "schema": scenario_schema,
                "strict": True,
                },
        }
    )

    data = json.loads(response.output_text)
    return data["interaction_description"], data["exit_flag"], data["options"]


