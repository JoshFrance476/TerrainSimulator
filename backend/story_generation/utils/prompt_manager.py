from pathlib import Path
import yaml
import json

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"
SCHEMAS_DIR = Path(__file__).parent.parent.parent / "schemas"


class PromptManager:
    """Manages system prompts and response schemas"""

    def __init__(self):
        self.prompts = {
            path.stem: yaml.safe_load(path.read_text(encoding="utf-8"))
            for path in PROMPTS_DIR.glob("*.yaml")
        }
        self.schemas = {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in SCHEMAS_DIR.glob("*.json")
        }

    def get(self, name: str) -> dict:
        if name not in self.prompts:
            raise KeyError(f"Unknown prompt: {name}")
        return self.prompts[name]

    def set(self, name: str, text: str = None, temperature: float = None,
            max_tokens: int = None, reasoning_effort: str = None):
        prompt = self.get(name)
        updates = {
            "system": text,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "reasoning_effort": reasoning_effort,
        }
        for key, value in updates.items():
            if value is not None:
                prompt[key] = value

    def get_schema(self, schema_name: str) -> dict:
        if schema_name not in self.schemas:
            raise KeyError(f"Unknown schema: {schema_name}")
        return self.schemas[schema_name]

    def load_response_format_schema(self, schema_name: str) -> dict:
        return {
            "type": "json_schema",
            "json_schema": {"name": schema_name, "schema": self.get_schema(schema_name)},
        }

    def load_tools_schema(self, *schema_names: str) -> list:
        tools = []
        for name in schema_names:
            # Shallow copy: schemas are cached now, so popping would mutate the
            # cached dict and break the second call.
            schema = dict(self.get_schema(name))
            function_name = schema.pop("_function_name")
            tools.append({
                "type": "function",
                "function": {"name": function_name, "parameters": schema},
            })
        return tools