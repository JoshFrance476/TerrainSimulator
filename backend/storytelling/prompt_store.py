from pathlib import Path
import yaml
import re

PROMPTS_DIR = Path(__file__).parent / "prompts"

_DEFAULT_SETTINGS = {
    "interaction": {"file_name": "scene_v2.yaml", "temperature": 1.0, "max_tokens": 800, "reasoning_effort": "low"},
    "scene-guide": {"file_name": "scene_setup_v2.yaml", "temperature": 0.7, "max_tokens": 800, "reasoning_effort": "medium"},
    "scene-summary": {"file_name": "scene_summary.yaml", "temperature": 0.7, "max_tokens": 400, "reasoning_effort": "low"},
}


def _render(template: str, variables: dict) -> str:
    def replacer(match):
        key = match.group(1)
        if key not in variables:
            raise KeyError(f"Template variable '{{{{ {key} }}}}' not provided")
        return str(variables[key])
    return re.sub(r'\{\{\s*(\w+)\s*\}\}', replacer, template)

def _load_system_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        messages = yaml.safe_load(f)
    for msg in messages:
        if msg["role"] == "system":
            return msg["content"]
    raise ValueError(f"No system message found in {filename}")

class Prompt:
    def __init__(self, name: str, text: str, temperature: float, max_tokens: int, reasoning_effort: str):
        self.name = name
        self.text = text
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.reasoning_effort = reasoning_effort

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "text": self.text,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "reasoning_effort": self.reasoning_effort
        }


class PromptStore:
    """Editable system-prompt templates and their model settings, held in memory
    for the session. Loaded from disk once at startup. Edits never write back to file."""

    def __init__(self):
        self.prompts = {}

        for name, settings in _DEFAULT_SETTINGS.items():

            self.prompts[name] = Prompt(
                name=name,
                text=_load_system_prompt(settings["file_name"]),
                temperature=settings["temperature"],
                max_tokens=settings["max_tokens"],
                reasoning_effort=settings["reasoning_effort"]
            )

    def get(self, name: str) -> Prompt:
        if name in self.prompts:
            return self.prompts[name]
        else:
            raise KeyError(f"Unknown prompt: {name}")

    def set(self, name: str, text: str, temperature: float = None, max_tokens: int = None, reasoning_effort: str = None):
        prompt = self.get(name)
        prompt.text = text
        if temperature is not None:
            prompt.temperature = temperature
        if max_tokens is not None:
            prompt.max_tokens = max_tokens
        if reasoning_effort is not None:
            prompt.reasoning_effort = reasoning_effort

    def render(self, name: str, variables: dict = None) -> str:
        return _render(self.get(name).text, variables or {})


