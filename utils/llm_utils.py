from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # loads .env into os.environ
import os
from config import WORLD_DESCRIPTION, STORY_PROMPT, CHARACTER_DESCRIPTION
import json

client = OpenAI(
    api_key= os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
"sk-553c67c3eeb6442ba324f3c72cd44998",

scenario_schema = [{
    "type": "function",
    "function": {
        "name": "generate_scenario",
        "description": "generate a scenario and a list of possible decisions",
        "parameters": {
            "type": "object",
            "properties": {
                "scenario_description": {"type": "string"},
                "options": {
                    "type": "array",
                    "description": "a list of 2-4 options that the user can choose",
                    "items": {
                        "type": "object",
                        "properties": {
                            "action": {"type": "string"}
                    }
                    }}
            },
            "required": ["scenario description", "options"],
            "additionalProperties": False
        }
    }
}]



def prompt_scenario(prompt, schema=scenario_schema, model="deepseek-chat", temperature = 1.5):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"""
            You are the storyteller in a single-player RPG game set on a 2D map made up of tiles.
            The user has defined the world context, their character and the type of stories they want to experience.
            You will be prompted to generate scenarios based on given context, which should be engaging for the user and should present a variety of decisions to make.
            Do not assume information about the world, it is represented to the user as a grid of coloured tiles.
            Scenarios should be no longer than 50 words, and each decision should be summarised in less than 15 words. 
            Keep the tone and content of scenarios consistent with the background that the user has provided.
            Here is the user-provided background:
            World context: {WORLD_DESCRIPTION},
            Character description: {CHARACTER_DESCRIPTION},
            Story prompt: {STORY_PROMPT}
            """},

            {"role": "user", "content": prompt}
        ],
        tools=schema,
        tool_choice={"type": "function", "function": {"name": schema[0]["function"]["name"]}},
        temperature=temperature,
        stream=False)

    scenario_text = json.loads(
        response.choices[0].message.tool_calls[0].function.arguments
        )["scenario_description"]
    
    scenario_actions = json.loads(
        response.choices[0].message.tool_calls[0].function.arguments
        )["options"]
    
    print(scenario_text, scenario_actions)

    return scenario_text, scenario_actions

