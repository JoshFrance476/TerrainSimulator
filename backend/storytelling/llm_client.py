from models import SceneContext, StorySetup
from storytelling.prompt_manager import PromptManager
from storytelling.log_writer import LogWriter
from huggingface_hub import AsyncInferenceClient
from huggingface_hub.errors import BadRequestError

from dataclasses import asdict

import json


class LLMClient:
    def __init__(self, state):
        self.client = AsyncInferenceClient()
        self.model = "Qwen/Qwen3-235B-A22B-Instruct-2507:novita"
        self.prompt_manager = PromptManager()
        self.log_writer = LogWriter()
        self.state = state 
 
    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _build(self, name: str, context: dict):
        """Assemble the messages and request kwargs for a prompt.   

        `context` is JSON-dumped as the user message.
        """
        prompt = self.prompt_manager.get(name)

        messages = [
            {"role": "system", "content": prompt["system"]},
            {"role": "user", "content": json.dumps(context)},
        ]

        kwargs = {
            "model": prompt.get("model", self.model),
            "temperature": prompt["temperature"],
            "max_tokens": prompt["max_tokens"],
            "extra_body": {"reasoning_effort": prompt["reasoning_effort"]},
        }
        if "response_schema" in prompt:
            kwargs["response_format"] = self.prompt_manager.load_response_format_schema(
                prompt["response_schema"]
            )
        if "tools" in prompt:
            kwargs["tools"] = self.prompt_manager.load_tools_schema(*prompt["tools"])
  
        return messages, kwargs

    def _record_usage(self, usage):
        if usage: 
            self.state.completion_tokens += usage.completion_tokens
            self.state.prompt_tokens += usage.prompt_tokens
        else:
            print("No usage data returned by provider") 

    async def _complete(self, name: str, context: dict):
        """Non-streaming request. Returns the raw response so callers can read
        either message.content or message.tool_calls."""
        messages, kwargs = self._build(name, context)
        self.log_writer.write_to_log(messages, label=f"{name.upper()} REQUEST")

        response = await self.client.chat.completions.create(messages=messages, **kwargs)

        self.log_writer.write_to_log(response.choices[0].message, label=f"{name.upper()} RESPONSE") 
        self._record_usage(response.usage)
        return response

    async def _complete_streaming(self, name: str, context: dict):
        messages, kwargs = self._build(name, context)
        self.log_writer.write_to_log(messages, label=f"{name.upper()} REQUEST")

        try:
            stream = await self.client.chat.completions.create(
                messages=messages,
                stream=True,
                stream_options={"include_usage": True},
                **kwargs,
            )
        except BadRequestError as e:
            print(e.response.text)
            raise

        reasoning_content = ""
        response_content = ""
        usage = None
        async for chunk in stream:
            if chunk.usage:
                usage = chunk.usage
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta
            reasoning = getattr(delta, "reasoning_content", None) 
            if reasoning:
                reasoning_content += reasoning
                yield {"reasoning": reasoning}
            if delta.content: 
                response_content += delta.content
                yield {"token": delta.content}

        self.log_writer.write_to_log({"role": "assistant", "content": response_content, "reasoning": reasoning_content}, label=f"{name.upper()} RESPONSE")
        self._record_usage(usage)
        yield {"content": response_content}

    # ------------------------------------------------------------------
    # Prompts
    # ------------------------------------------------------------------

    async def prompt_interaction(self, guide, previous_interactions):
        context = {
            "guide": guide, 
            "previous_interactions": previous_interactions,
            "story_setup": asdict(self.state.story_setup)
        } 

        async for event in self._complete_streaming("interaction", context):
            if "token" in event:
                yield {"event": "token", "payload": event["token"]}
            else:
                data = event["content"]
                yield {"event": "done", "payload": data}

    async def prompt_storylines(self, setup: StorySetup, component_lookup, region_lookup):
        context = {
            "world_description": setup.world_description,
            "story_focus_description": setup.story_focus_description,
            "character_description": setup.character_description,
            "regions": region_lookup
        }
        async for event in self._complete_streaming("storylines", context):
            if "token" in event:
                yield {"event": "token", "payload": event["token"]} 
            elif "reasoning" in event:
                yield {"event": "reasoning", "payload": event["reasoning"]}
            else:
                yield {"event": "done", "payload": event["content"]}

    async def prompt_scene_guide(self, scene_context: SceneContext, scene_history: list[dict], significance: str):
        context = {
            "location_context": asdict(scene_context.tile_data),
            "significance": significance,
            "character_notebook": scene_context.character_notebook,
            "scene_history": scene_history,
            "story_setup": asdict(scene_context.story_setup),
        }
        async for event in self._complete_streaming("scene-guide", context):
            if "token" in event:
                yield {"event": "token", "payload": event["token"]}
            else:
                data = event["content"]
                yield {"event": "done", "payload": data}

    async def prompt_hidden_context(self, storylines, component_lookup, region_lookup):
        context = {
            "storylines": storylines.storylines,
            "components": component_lookup,
            "regions": region_lookup
        }
        response = await self._complete("context", context)
        return json.loads(response.choices[0].message.content)

    async def prompt_scene_summary(self, scene):
        context = {"scene": scene.to_dict()}
        response = await self._complete("scene-summary", context)
        return json.loads(response.choices[0].message.content)
    
