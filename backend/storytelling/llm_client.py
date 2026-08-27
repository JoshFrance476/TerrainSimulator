from models import SceneContext
from storytelling.prompt_manager import PromptManager
from storytelling.log_writer import LogWriter
from huggingface_hub import AsyncInferenceClient

from dataclasses import asdict

import json


class LLMClient:
    def __init__(self, state):
        self.client = AsyncInferenceClient()
        self.model = "Qwen/Qwen3-235B-A22B-Instruct-2507:novita"
        self.prompt_manager = PromptManager()
        self.log_writer = LogWriter()
        self.state = state

    def _settings_kwargs(self, name):
        prompt = self.prompt_manager.get(name)
        return {
            "model": self.model,
            "temperature": prompt.temperature,
            "max_tokens": prompt.max_tokens,
            "extra_body": {"reasoning_effort": prompt.reasoning_effort},
        }


    async def prompt_interaction(self, guide, previous_interactions):
        messages = [
            {"role": "system", "content": self.prompt_manager.render("interaction", asdict(self.state.story_setup))},
            {"role": "user", "content": json.dumps({
                "guide": guide,
                "previous_interactions": previous_interactions
            })}
        ] 

        stream_response = await self.client.chat.completions.create(
            messages=messages,
            stream=True,
            stream_options={"include_usage": True},
            response_format=self.prompt_manager.load_response_format_schema("scene"),
            **self._settings_kwargs("interaction")
        )

        print(json.dumps({"messages": messages, **self._settings_kwargs("interaction")}, indent=2))

        full_response = ""
        final_chunk = None
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
            self.log_writer.write_to_log({**self._settings_kwargs("interaction")})
            self.log_writer.write_to_log(data, label="INTERACTION RESPONSE")

            print(final_chunk)

            result = {
                "description": data["interaction_description"],
                "actions": data["player_actions"],
            }

            if final_chunk:
                self.state.completion_tokens += final_chunk.usage.completion_tokens
                self.state.prompt_tokens += final_chunk.usage.prompt_tokens
            else:
                print("No usage data returned by provider")

            yield {"data": json.dumps(result), "event": "done"}

        except json.JSONDecodeError as e:
            yield {"data": json.dumps({"error": "Invalid JSON from model", "detail": str(e)}), "event": "stream_error"}

        except KeyError as e:
            yield {"data": json.dumps({"error": "Unexpected response schema", "missing_key": str(e)}), "event": "stream_error"}

        except Exception as e:
            yield {"data": json.dumps({"error": "Stream failed", "detail": str(e)}), "event": "stream_error"}
            raise


    async def prompt_scene_setup(self, scene_context: SceneContext, scene_history: list[dict], significance: str):
            context = {
                "location_context": asdict(scene_context.tile_data),
                "significance": significance,
                "character_notebook": scene_context.character_notebook,
                "scene_history": scene_history
            }
    
            if scene_history:
                first_scene = scene_history[0]
                context["scene_trigger"] = first_scene['chosen_action']

            messages = [
                {"role": "system", "content": self.prompt_manager.render("scene-guide", asdict(scene_context.story_setup))},
                {"role": "user", "content": json.dumps({
                    "context": context,
                })},
            ]
            
            response = await self.client.chat.completions.create(
                messages=messages,
                response_format=self.prompt_manager.load_response_format_schema("scene_setup"),
                **self._settings_kwargs("scene-guide")
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
            
            self.log_writer.write_to_log(messages, label="SCENE GUIDE REQUEST")
            self.log_writer.write_to_log({**self._settings_kwargs("scene-guide")})
            self.log_writer.write_to_log(data, label="SCENE GUIDE RESPONSE")

            if response.usage:
                self.state.completion_tokens += response.usage.completion_tokens
                self.state.prompt_tokens += response.usage.prompt_tokens
            
            return {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "guide": data
            }

    async def prompt_scene_summary(self, scene, chunk_list):
        context = {
            "scene": scene,
            "chunk_list": chunk_list
        }

        messages = [
            {"role": "system", "content": self.prompt_manager.render("scene-summary")},
            {"role": "user", "content": json.dumps(context)}
        ]
        
        response = await self.client.chat.completions.create(
            messages=messages,
            tools=self.prompt_manager.load_tools_schema("quest", "summary"),
            **self._settings_kwargs("scene-summary")
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

        self.log_writer.write_to_log(messages, label="SCENE SUMMARY REQUEST")
        self.log_writer.write_to_log({**self._settings_kwargs("scene-summary")})
        self.log_writer.write_to_log(response.choices[0].message, label="SCENE SUMMARY RESPONSE")

        if response.usage:
            self.state.completion_tokens += response.usage.completion_tokens
            self.state.prompt_tokens += response.usage.prompt_tokens

        return {
            "summary": summary,
            "new_quests": new_quests
        }
