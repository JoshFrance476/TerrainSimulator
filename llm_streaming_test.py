import time
import json
from httpx import stream
from huggingface_hub import InferenceClient

client = InferenceClient()
model = "openai/gpt-oss-120b"

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

scene_structure_message = [
    {
        "role": "system",
        "content": """You generate scene graphs for a text-based open-world game, as Mermaid flowcharts.

VOCABULARY
- Situation node: one beat of gameplay. A single third-person sentence
  describing what the player sees or what has just happened. This text is
  shown directly to the player.
- Action edge: one thing the player may choose to do from a situation node.
  Actions are ALWAYS edge labels. Never create a node for a choice or question.
- Outcome node: a terminal state that ends the scene. Every path ends in one.

GRAPH SHAPE (follow exactly)
- One root situation node, id S0, describing the precise_location.
- Treat each outcome_suggestion as the THEME of one top-level branch, not as a
  literal ending. S0 has exactly one action edge per outcome_suggestion, in the
  order given, each leading to the first situation node of that branch.
- Each branch is a chain of exactly 3 situation nodes.
- Every non-root situation node has exactly 2 action edges.
  - For the 1st and 2nd node in a chain: one edge continues to the next
    situation node in that chain, the other edge leads to an outcome node.
  - For the 3rd node in a chain: both edges lead to outcome nodes.
- This yields exactly 10 situation nodes, 12 outcome nodes, 21 action edges.
- The graph is a tree. Branches never rejoin. There are no cycles.
- Every leaf is an outcome node. Every node is reachable from S0.

SYNTAX CONTRACT
- Output a single fenced block: ```mermaid, then flowchart TD, then the graph,
  then a closing fence. Output nothing else — no prose, no comments, no
  subgraphs, no styling, no %% lines.
- Situation node:  S3["Text here."]
- Outcome node:    E2["Outcome: text here."]
- Action edge:     S3 -->|Short action phrase| S4
- IDs are S0..Sn and E1..En. Each ID is defined exactly once.
- Label text: plain ASCII only. No double quotes, parentheses, square or curly
  brackets, pipes, hashes, semicolons, curly/smart quotes, or line breaks
  inside a label. No dialogue in quotation marks — paraphrase it instead.
- Situation text: max 25 words. Action labels: 2 to 6 words, imperative,
  and distinct from each other within the same node.

INPUT HANDLING
- previous_interactions lists what has already happened in this scene. If it is
  non-empty, S0 must continue from the last entry and must not repeat it.
"""
    },
    {
        "role": "user",
        "content": json.dumps({
            "scene_guide": {
                "environment_description": "The Lord's Castle looms atop a high hill in the town, its stone walls weathered but imposing, surrounded by open plains that stretch in all directions.",
                "precise_location": "The main gate of the castle is guarded by two armored soldiers, a heavy oak door slightly ajar behind them.",
                "story_suggestion": "The player attempts to enter the castle grounds but is confronted by guards enforcing strict access rules.",
                "outcome_suggestions": ["A guard stops the player from entering and demands a service in return for access", "The player observes a commotion at the gate — a messenger arrives with urgent news", "The player is turned away by guards but overhears a conversation about unrest in the town"]
            }
        })
    }
]

component_list_example = {
    "regions": [{"title": "Akhira", 
            "description": "Akhira is a small walled town, serving as a trading center for the surrounding area.",
            "places": {
                "1": {"name": "Church", "description": "An old stone church"},
                "2": {"name": "Tavern", "description": "A large two-storey tavern with rooms to rent"},
                "3": {"name": "Castle", "description": "Sitting just outside the town walls, its large archway entrance is an imposing structure"},
                "4": {"name": "House", "description": ""},
                "5": {"name": "House", "description": ""},
                "6": {"name": "House", "description": ""},
                "7": {"name": "House", "description": ""},
}}]}

story_setup = {
    "world_description": "An arcade-style medieval world. The world is grounded in reality and does not contain fantasy elements.",
    "story_focus": "The player's goal is to make a name for themself",
    "character_description": "A young knight"
}

storylines = [
    "Rival merchant families vie for control of the town’s market",
    "A sacred relic has vanished from the Church.",
    "Bandits have begun raiding the outskirts of Akhira."
]

compiler_message = [{
    "role": "system",
    "content": """
You are part of a story generation system for an arcade-style open-world procedural story game. 
You will be given a comprehensive list of every notable place in the world, and your task is to add relevant story context to each place.
You will be provided with a list of storylines. This is what you should base story context off.
Return the JSON you are given with an added "context" field to each place.
The context field should be list of short prompts that build the storylines into the world.
    """
},{
    "role": "user", "content": f"STORY SETUP:\n{storylines}\n\nPLACES:\n{json.dumps(component_list_example)}"
}]


def run_stream(messages, max_tokens, temperature):
    start = time.time()
    first_token_time = None

    stream = client.chat.completions.create(
        model=model,
        max_tokens=max_tokens,
        messages=messages,
        stream=True,
        temperature=temperature,
        stream_options={"include_usage": True}
    )

    usage = None
    for chunk in stream:
        if chunk.usage:
            usage = chunk.usage
        if not chunk.choices:
            print(repr(chunk))
            continue
        d = chunk.choices[0].delta
        fr = chunk.choices[0].finish_reason
        if fr:
            print(f"\n[finish_reason={fr}]")
        text = getattr(d, "content", None) or getattr(d, "reasoning_content", None)
        if text:
            if first_token_time is None:
                first_token_time = time.time()
                print(f"TTFT: {first_token_time - start:.2f}s")
            print(text, end="", flush=True)
        
        if usage:
            print(repr(usage))


run_stream(compiler_message, max_tokens=5000, temperature=0.3)
#run_stream(interaction_message, max_tokens=250, temperature=0.7)