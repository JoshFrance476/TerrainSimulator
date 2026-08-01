from storytelling.prompt_loader import PromptLoader
from storytelling.prompt_store import PromptStore
from storytelling.log_writer import LogWriter
from huggingface_hub import AsyncInferenceClient
import json


class LLMClient:
    def __init__(self, state):
        self.client = AsyncInferenceClient()
        self.model = "Qwen/Qwen3-235B-A22B-Instruct-2507:novita"
        self.loader = PromptLoader()
        self.prompts = PromptStore()
        self.log_writer = LogWriter()
        self.state = state

        self.interaction_prompt_filename = "scene_v2"
        self.scene_guide_prompt_filename = "scene_setup_v2"


    

    async def prompt_interaction(self, guide, previous_interactions):
        messages = [
            {"role": "system", "content": self.prompts.render("interaction",
                                                              {"world_desc": self.state.world_desc,
                                                               "story_focus_desc": self.state.story_focus_desc,
                                                               "character_desc": self.state.character_desc})},
            {"role": "user", "content": json.dumps({
                "guide": guide,
                "previous_interactions": previous_interactions
            })}
        ]

        stream_response = await self.client.chat.completions.create(
            model=self.model,
            temperature=1,
            max_tokens=800,
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            response_format=self.loader.load_response_format_schema("scene"),
            extra_body={"reasoning_effort": "low"},
        )

        full_response = ""
        try:
            async for chunk in stream_response:
                if chunk.usage:
                    final_chunk = chunk
                if not chunk.choices:
                    continue

                token = chunk.choices[0].delta.content 
                if token:
                    full_response += token
                    yield {"data": token, "event": "data"}

            data = json.loads(full_response)

            self.log_writer.write_to_log(messages, label="INTERACTION REQUEST")
            self.log_writer.write_to_log(data, label="INTERACTION RESPONSE")

            print(final_chunk)

            result = {
                "description": data["interaction_description"],
                "actions": data["actions"],
            }

            if final_chunk.usage:
                self.state.completion_tokens += final_chunk.usage.completion_tokens
                self.state.prompt_tokens += final_chunk.usage.prompt_tokens
            else:
                print("No usage data returned by provider")

            yield {"data": json.dumps(result), "event": "done"}

        except json.JSONDecodeError as e:
            yield {"data": json.dumps({"error": "Invalid JSON from model", "detail": str(e)}), "event": "error"}

        except KeyError as e:
            yield {"data": json.dumps({"error": "Unexpected response schema", "missing_key": str(e)}), "event": "error"}

        except Exception as e:
            yield {"data": json.dumps({"error": "Stream failed", "detail": str(e)}), "event": "error"}
            raise


    async def prompt_scene_setup(self, context, significance, notebook, scene_history):
            context = {
                "location_context": context,
                "significance": significance,
                "character_notebook": notebook,
                "scene_history": scene_history
            }
    
            if scene_history:
                first_scene = scene_history[0]
                context["scene_trigger"] = first_scene['chosen_action']

            messages = [
                {"role": "system", "content": self.prompts.render("scene-guide",
                                                                  {"world_desc": self.state.world_desc,
                                                                    "story_focus_desc": self.state.story_focus_desc,
                                                                    "character_desc": self.state.character_desc})},
                {"role": "user", "content": json.dumps({
                    "context": context,
                })},
            ]
            
            response = await self.client.chat.completions.create(
                model=self.model,
                temperature=0.7,
                max_tokens=800,
                messages=messages,
                response_format=self.loader.load_response_format_schema("scene_setup"),
                extra_body={"reasoning_effort": "medium"},
            )

            print(response)
    
            raw_output = response.choices[0].message.content
            try:
                data = json.loads(raw_output)
            except json.JSONDecodeError as e:
                print(f"JSON parse failed: {e}")
                print(f"completion_tokens used: {response.usage.completion_tokens}")
                print(f"finish_reason: {response.choices[0].finish_reason}")
                print(f"raw content: {raw_output!r}")
                raise
            
            self.log_writer.write_to_log(messages, label="SCENE REQUEST")

            if response.usage:
                self.state.completion_tokens += response.usage.completion_tokens
                self.state.prompt_tokens += response.usage.prompt_tokens
            
            return {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "guide": data
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
            "story_list": data["story_list"]
        }

    async def prompt_scene_summary(self, scene, chunk_list):
        messages = self.loader.load_messages("scene_summary", {
            "scene": scene,
            "chunk_list": str(chunk_list)
        })
        response = await self.client.chat.completions.create(
            model=self.model,
            temperature=0.7,
            max_tokens=400,
            messages=messages,
            tools=self.loader.load_tools_schema("quest", "summary"),
            extra_body={"reasoning_effort": "low"},
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

        if response.usage:
            self.state.completion_tokens += response.usage.completion_tokens
            self.state.prompt_tokens += response.usage.prompt_tokens

        return {
            "summary": summary,
            "new_quests": new_quests
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
