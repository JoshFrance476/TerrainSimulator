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

narrative_schema_with_storyline = [{
    "type": "function",
    "function": {
        "name": "generate_narrative",
        "description": "Generate a narrative and storyline for event",
        "parameters": {
            "type": "object",
            "properties": {
                "narrative": {"type": "string",
                              "description": f"A short creative description of the event inspired by {LLM_THEME}"},
                "storyline": {"type": "string",
                              "description": f"A storyline that the event takes place in"},
                "storyline_scope": {"type": "string",
                                    "enum": ["settlement", "biome", "continent","global"]},
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
            "required": ["narrative", "actions", "storyline", "storyline_scope"],
            "additionalProperties": False
        }
    }
}]


narrative_schema = [{
    "type": "function",
    "function": {
        "name": "generate_narrative",
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


def prompt_narrative(prompt, with_storyline, model="deepseek-chat", temperature=1.5):
    if with_storyline:
        schema = narrative_schema_with_storyline
    else:
        schema = narrative_schema
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": f"""
            You are the worldbuilder of a procedurally generated world.
            The user has given the world theme as '{LLM_THEME}'. All narratives and storylines should be relevant to the world theme.
            Write one narrative in the world based on the given event, relevant storylines and environment context.
            Narratives should be vivid and bring life to the world.
            Do not describe singular moments, gestures, or symbolic imagery. Focus on structural outcomes.
            Do not generate proper nouns unless they appear in the prompt.
            If the event is unspecified, you have creative freedom to generate a narrative, but it must be based solely on the given context and world theme.
            Narratives should be no longer than 50 words.
            Keep the tone consistent with the themes culture, technology, and politics.
            Return JSON with 'narrative', 'actions', 'storyline' and 'storyline_scope'.
            Storylines should be no longer than 20 words and provide a summary of circumstances in which the narrative takes place.
            Storyline scope should define the area in which the storyline takes place, and can be 'settlement', 'biome', 'continent' or 'worldwide'.
            If a storyline is provided in the prompt, it should be updated to reflect any changes the narrative has made to the story.
            Here is a list of possible actions:
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
    if with_storyline:
        storyline = json.loads(
            response.choices[0].message.tool_calls[0].function.arguments
    )["storyline"]
        storyline_scope = json.loads(
            response.choices[0].message.tool_calls[0].function.arguments
    )["storyline_scope"]
    else:
        storyline = None
        storyline_scope = None
    cache_hits = response.usage.prompt_cache_hit_tokens
    cache_misses = response.usage.prompt_cache_miss_tokens
    completion_tokens = response.usage.completion_tokens
    print(f"Cache hits: {cache_hits}, cache misses: {cache_misses}, output tokens: {completion_tokens}")
    cost = (((cache_hits/1000000) * 0.028) + ((cache_misses/1000000) * 0.28) + ((completion_tokens/1000000) * 0.42)) * 0.75 * 100
    print(f"Cost = {cost:.4f}p")
    return desc, actions, storyline, storyline_scope



if __name__ == "__main__":
    desc, actions, storyline, storyline_scope = prompt_narrative(
        """
        A unspecified event has occured
        """,
        True
    )
    print(desc, actions, storyline, storyline_scope)
