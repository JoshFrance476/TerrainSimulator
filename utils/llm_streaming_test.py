import time
from together import Together
import json

client = Together()

start = time.time()
first_token_time = None

interaction_message = [
    {
        "role": "system",
        "content": """You are the storyteller in an arcade-style story game set within a procedurally-generated world.
Your task is to turn the scene guide you are given into a concise narrative to present to the player.

CONTEXT
You will receive:
- scene_guide: A general guide for the next step in the scene.
- scene_history: A chronological account of what has already occured in the scene.

OUTPUT RULES
- Write the scene guide into second-person narrative prose. 150 words max.
- The user is roleplaying as the character. Present the scene to their character.
- Ensure not to skip details from the story suggestion and include details from precise_location and environment_description that will immerse the player in the scene.
- Don't repeat what has already been described in the scene_history.
- Provide one action per outcome suggestion that could plausibly lead to it. Actions can be physical, observational, conversational, or instinctive — whatever fits the scene naturally.
- Actions must accurately describe the character's action that would lead to the outcome suggestion.
- Ensure there is one action per outcome suggestion.
- If the outcome suggestion ends the scene, set exit_flag: True for the action.
- Each action must be under 15 words.

WRITING STYLE
- Prose must be plain and observational. Avoid cinematic staging clichés (e.g. "leans in", "voice low", "eyes scanning", "pauses meaningfully").
- Describe what literally happens, not how a film would frame it.
- NPC speech should sound like an ordinary person, not a dramatic character.
- Favour concrete nouns over atmospheric adjectives.

World description: The map focuses on a mysterious continent that has begun to be colonised by a british-empire like civilisation. The continent was untouched by humans until it began to be colonised. The coast is largely plains, but the interior is covered in dense forests and huge mountain ranges. Only two major towns sit on the coastline, and the interior is unexplored. Contact with the empire is rare and the colonists are only just starting to discover the strange creatures that populate the continent interior. The settled coastline is growing quickly with new colonists arriving frequently, but fear and curiosity is spreading about the interior.
Story focus: A grounded survival story focusing on the player interacting with the locals and exploring the continent interior to discover its mysteries."""
    },
    {
        "role": "user",
        "content": json.dumps({
            "guide": {
                "environment_description": "The vast open plains stretch eastward toward distant forests and mountains, bordered by a fortified city wall to the south and southeast, with a gate and road cutting through the otherwise isolated landscape.",
                "precise_location": "The character stands on short, dry grass just west of a dirt road that runs perpendicular to a large stone city wall, where a wooden gatehouse is visible in the distance.",
                "story_suggestion": "A local guard halts the player at the gate, questioning their intent to leave the settlement, while signs of an animal trail vanish into the plains beyond.",
                "outcome_suggestions": [
                    "The guard allows passage after inspecting the player's gear, granting access to the eastern plains and forest beyond",
                    "The guard refuses entry, citing recent sightings of strange creatures, forcing the player to find another way out",
                    "The player notices a broken section of wall nearby and chooses to slip past unnoticed",
                    "The guard mentions a missing scout last seen heading into the forest, offering a reward for information — ends scene"
                ]
            },
            "previous_interactions": []
        })
    }
]

scene_message = [
    {
        "role": "system",
        "content": """You goal is to generate scene guides for an arcade-style story game.
Your task it to turn the context you are given into a short guide for a scene.
The guide should contain any relevant information for the scene, as well as suggestions for the story.
Scenes should be grounded within the context but creative.
The story suggestion and potential outcomes must be feasible for a short scene in the current location.
If any context contains instructions, prioritise these instructions.
All descriptions must be grounded and literal.
If a scene trigger is provided, treat it as the inciting moment that opens this scene.
The scene history is a full log of previous events in the scene, with the first being the most recent.
Ensure that the scene trigger has a meaningful impact on this scene.
If an outcome involves moving on from the current scene, add 'ends scene' to the end of the description. Otherwise don't put anything.
Dramatic elements in the story suggestion must be grounded in provided context or scene history — never invented from genre conventions.

The guide must contain:
1. Environment description - A single sentence describing the broader environment based on given context.
2. Precise location - A single sentence describing the immediate, close-range details of the specific spot
3. Story suggestion - A single sentence suggesting what the player could encounter in the scene - based on scene significance.
4. A short list of potential outcomes of the scene

WORLD CONTEXT:
  World description: The map focuses on a mysterious continent that has begun to be colonised by a british-empire like civilisation. The continent was untouched by humans until it began to be colonised. The coast is largely plains, but the interior is covered in dense forests and huge mountain ranges. Only two major towns sit on the coastline, and the interior is unexplored. Contact with the empire is rare and the colonists are only just starting to discover the strange creatures that populate the continent interior. The settled coastline is growing quickly with new colonists arriving frequently, but fear and curiosity is spreading about the interior.
  Story focus: A grounded survival story focusing on the player interacting with the locals and exploring the continent interior to discover its mysteries.
  Character description: An explorer who has just arrived on the continent. They have a backpack with a set of useful exploring tools. They were inspired by reports of strange fauna and have come to investigate. They are well-received by locals, who can sense the determination of the character."""
    },
    {
        "role": "user",
        "content": json.dumps({
            "location_context": {
                "nearby_chunks": [
                    {"direction": "east", "biome": "Road", "chunk_id": 676},
                    {"direction": "east", "biome": "plains", "chunk_id": 570},
                    {"direction": "east", "biome": "forest", "chunk_id": 546},
                    {"direction": "east", "biome": "plains", "chunk_id": 583},
                    {"direction": "north-west", "biome": "plains", "chunk_id": 574},
                    {"direction": "east", "biome": "Wall Gate", "chunk_id": 711},
                    {"direction": "east", "biome": "City Wall", "chunk_id": 660},
                    {"direction": "south-east", "biome": "City Wall", "chunk_id": 663},
                    {"direction": "south", "biome": "City Wall", "chunk_id": 665}
                ],
                "current_tile": {"Biome": "plains", "Biome Description": "", "Details": {}},
                "recent_movement": {"direction": "west", "from_biome": "Road", "to_biome": "plains"}
            },
            "significance": "High",
            "character_notebook": [],
            "scene_history": []
        })
    }
]

stream = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
    max_tokens=300,
    messages=scene_message,
    stream=True,
    temperature=1
)

for chunk in stream:
    if chunk.choices:
        if first_token_time is None:
            first_token_time = time.time()
            print(f"Time to first token: {first_token_time - start:.2f}s")
        print(chunk.choices[0].delta.content, end="", flush=True)

end = time.time()
print(f"\nTotal time: {end - start:.2f}s")

stream = client.chat.completions.create(
    model="Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
    max_tokens=250,
    messages=interaction_message,
    stream=True,
    temperature=0.7
)

for chunk in stream:
    if chunk.choices:
        if first_token_time is None:
            first_token_time = time.time()
            print(f"Time to first token: {first_token_time - start:.2f}s")
        print(chunk.choices[0].delta.content, end="", flush=True)

end = time.time()
print(f"\nTotal time: {end - start:.2f}s")