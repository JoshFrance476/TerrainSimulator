from storytelling.prompt_loader import PromptLoader
from together import Together
import json


class StoryLLM:
    def __init__(self):
        self.client = Together()
        self.model = "openai/gpt-oss-120b"
        self.loader = PromptLoader()

    def prompt_scene(self, context, world_desc, story_focus_desc):
        messages = self.loader.load_messages("scene", {
            "context": context,
            "world_desc": world_desc,
            "story_focus_desc": story_focus_desc
        })
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=600,
            reasoning_effort="low",
            messages=messages,
            response_format=self.loader.load_response_format_schema("scene")
        )
        data = json.loads(response.choices[0].message.content)
        print(response)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "description": data["interaction_description"],
            "actions": data["actions"]
        }

    def prompt_story_setup(self, character_desc, world_desc, story_focus_desc):
        messages = self.loader.load_messages("story_setup", {
            "character_desc": character_desc,
            "world_desc": world_desc,
            "story_focus_desc": story_focus_desc
        })
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            max_tokens=2000,
            reasoning_effort="medium",
            messages=messages,
            response_format=self.loader.load_response_format_schema("story_setup")
        )
        data = json.loads(response.choices[0].message.content)
        print(response)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "story_list": data["story_list"]
        }

    def prompt_scene_summary(self, scene, chunk_list):
        messages = self.loader.load_messages("scene_summary", {
            "scene": scene,
            "chunk_list": str(chunk_list)
        })
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=400,
            reasoning_effort="low",
            messages=messages,
            tools=self.loader.load_tools_schema("quest", "summary"),
        )
        summary = None
        print(response)
        new_quests = []

        for tool_call in (response.choices[0].message.tool_calls or []):
            args = json.loads(tool_call.function.arguments)
            if tool_call.function.name == "generate_summary":
                summary = args.get("summary")
            elif tool_call.function.name == "add_quest":
                new_quests.append({
                    "chunk_id": args.get("chunk_id"),
                    "title": args.get("title"),
                    "visible_description": args.get("visible_description"),
                    "hidden_description": args.get("hidden_description")
                })

        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "summary": summary,
            "new_quests": new_quests
        }

    def prompt_scene_setup(self, context, world_desc, story_focus_desc, character_desc, significance):
        messages = self.loader.load_messages("scene_setup", {
            "context": context,
            "world_desc": world_desc,
            "story_focus_desc": story_focus_desc,
            "character_desc": character_desc,
            "significance": significance
        })
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=800,
            reasoning_effort="medium",
            messages=messages,
            response_format=self.loader.load_response_format_schema("scene_setup")
        )
        data = json.loads(response.choices[0].message.content)
        print(response)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "focus": data["scene_prompt"],
            "environment": data["environment_description"]
        }

    def prompt_character_setup(self, character_desc, world_desc, story_focus_desc):
        messages = self.loader.load_messages("character_setup", {
            "character_desc": character_desc,
            "world_desc": world_desc,
            "story_focus_desc": story_focus_desc,
            "schema_json": json.dumps(self.loader.load_raw_schema("character_setup"))
        })
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            max_tokens=800,
            reasoning_effort="low",
            messages=messages,
            response_format=self.loader.load_response_format_schema("character_setup")
        )
        print(response)
        data = json.loads(response.choices[0].message.content)
        return {
            "completion_tokens": response.usage.completion_tokens,
            "prompt_tokens": response.usage.prompt_tokens,
            "notebook": data["notebook_list"],
            "attributes": data["attribute_list"]
        }
