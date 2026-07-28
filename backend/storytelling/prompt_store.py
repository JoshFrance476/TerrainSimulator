from pathlib import Path
import yaml
from storytelling.prompt_loader import _render

PROMPTS_DIR = Path(__file__).parent / "prompts"

_SOURCE_FILES = {
    "interaction": "scene_v2.yaml",
    "scene-guide": "scene_setup_v2.yaml",
}


def _load_system_prompt(filename: str) -> str:
    with open(PROMPTS_DIR / filename, "r", encoding="utf-8") as f:
        messages = yaml.safe_load(f)
    for msg in messages:
        if msg["role"] == "system":
            return msg["content"]
    raise ValueError(f"No system message found in {filename}")


class PromptStore: 
    """Editable system-prompt templates, held in memory for the session.
    Loaded from disk once at startup. Edits never write back to file."""

    def __init__(self):
        self._prompts = {
            name: _load_system_prompt(filename)
            for name, filename in _SOURCE_FILES.items()
        }

    def get(self, name: str) -> str:
        if name not in self._prompts:
            raise KeyError(f"Unknown prompt: {name}")
        return self._prompts[name]

    def set(self, name: str, text: str):
        if name not in self._prompts:
            raise KeyError(f"Unknown prompt: {name}")
        self._prompts[name] = text

    def render(self, name: str, variables: dict) -> str:
        return _render(self.get(name), variables)