from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()  # loads .env into os.environ
import os
from config import LLM_ACTIONS_NAMES, LLM_THEME
import json

client = OpenAI(
    api_key= os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)
"sk-553c67c3eeb6442ba324f3c72cd44998",
"""
Given current token usage, we can get 10,000 responses from $1 (£0.82)
That's with output being one sentence and minimal context
Using ~50 tokens per response, 64 cache hits and 22 cache misses

Can either double response size, or ~quadruple input and still get 5,000 responses per $1
"""

event_schema = [{
    "type": "function",
    "function": {
        "name": "generate_event",
        "description": "Generate an event with description and effects",
        "parameters": {
            "type": "object",
            "properties": {
                "description": {"type": "string"},
                "coords": {"type": "array",
                           "items": {"type": "integer"},
                            "minItems": 2,
                            "maxItems": 2},
                "effects": {"type": "object",
                        "properties": {
                            "population": {"type": "integer"},
                }}},
            "required": ["description", "effects"]
        }
    }
}]


desc_schema = [{
    "type": "function",
    "function": {
        "name": "generate_description",
        "description": "Generate a narrative for event",
        "parameters": {
            "type": "object",
            "properties": {
                "narrative": {"type": "string",
                              "description": f"A short creative description of the event inspired by {LLM_THEME}"},
                "actions": {"type": "array",
                            "items": {"type": "object",
                                      "properties": {
                                          "action": {"type": "string",
                                                     "enum": LLM_ACTIONS_NAMES},
                                          "impact": {"type": "string",
                                                     "enum": ["low", "medium", "high"]}
                                      },
                                      "required": ["action", "impact"],
                                      "additionalProperties": False
                                    }
                           }
            },
            "required": ["narrative", "actions"],
            "additionalProperties": False
        }
    }
}]


def ask_deepseek(prompt, schema, model="deepseek-chat", temperature=1.5):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"""
             You are the worldbuilder of a realistic world simulation.
            The world is based on {LLM_THEME}.
            Write one grounded narrative in that world. The narrative should describe the given event.
            If the event is unspecified, you have creative freedom to generate a narrative, but it must be based solely on the given context and world theme.
            Narratives should be no longer than 50 words.
            Keep the tone consistent with the themes culture, technology, and politics.
            Return JSON with 'narrative' and 'actions'.
            Here is a list of possible actions. Actions can be left empty.
             {LLM_ACTIONS_NAMES}"""},

            {"role": "user", "content": prompt}
        ],
        tools=schema,
        tool_choice={"type": "function", "function": {"name": schema[0]["function"]["name"]}},
        temperature=temperature,
        stream=False
    )
    desc = json.loads(
        response.choices[0].message.tool_calls[0].function.arguments
    )["narrative"]
    actions = json.loads(
        response.choices[0].message.tool_calls[0].function.arguments
    )["actions"]
    return desc, actions
