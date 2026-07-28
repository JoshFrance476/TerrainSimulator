from pathlib import Path
import json
import re
import yaml

PROMPTS_DIR = Path(__file__).parent / "prompts"
SCHEMAS_DIR = Path(__file__).parent.parent / "schemas"


def _render(template: str, variables: dict) -> str:
    def replacer(match):
        key = match.group(1).strip()
        if key not in variables:
            raise KeyError(f"Template variable '{{{{ {key} }}}}' not provided")
        return str(variables[key])
    return re.sub(r'\{\{(\w+)\}\}', replacer, template)


class PromptLoader:
    """Loads non-editable prompts (scene_summary, story_setup, character_setup)
    and schemas straight from disk. Unrelated to editable system prompts —
    see PromptStore for those."""

    def load_messages(self, prompt_name: str, variables: dict) -> list:
        path = PROMPTS_DIR / f"{prompt_name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            messages = yaml.safe_load(f)
        return [{"role": m["role"], "content": _render(m["content"], variables)} for m in messages]

    def load_response_format_schema(self, schema_name: str) -> dict:
        schema = self.load_raw_schema(schema_name)
        return {"type": "json_schema", "json_schema": {"name": schema_name, "schema": schema}}

    def load_tools_schema(self, *schema_names: str) -> list:
        tools = []
        for name in schema_names:
            schema = self.load_raw_schema(name)
            function_name = schema.pop("_function_name")
            tools.append({"type": "function", "function": {"name": function_name, "parameters": schema}})
        return tools

    def load_raw_schema(self, schema_name: str) -> dict:
        path = SCHEMAS_DIR / f"{schema_name}.json"
        if not path.exists():
            raise FileNotFoundError(f"Schema file not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)