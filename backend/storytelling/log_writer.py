from pathlib import Path
from datetime import datetime
from config import MAP_NAME
import yaml
import json


LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"

class LogWriter:
    def __init__(self):
        self.log_file_name = None 
        self.now = datetime.now()
        self.map_name = MAP_NAME if MAP_NAME else "Procedural"
    
    def write_to_log(self, message, label=None):
        if not self.log_file_name:
            self.log_file_name = self.map_name + "_" + self.now.strftime("%Y-%m-%d_%H-%M-%S") + ".yaml"
        path = LOG_DIR
        path.mkdir(parents=True, exist_ok=True)

        with open(path / self.log_file_name, "a", encoding="utf-8") as f:
            if label:
                f.write(f"\n# --- {label} ---\n")
            if isinstance(message, list):
                for msg in message:
                    content = msg['content']
                    try:
                        content = json.loads(content)
                        content_str = yaml.dump(content, sort_keys=False, allow_unicode=True, indent=2)
                        f.write(f"- role: {msg['role']}\n  content:\n")
                        for line in content_str.splitlines():
                            f.write(f"    {line}\n")
                    except (json.JSONDecodeError, TypeError):
                        f.write(f"- role: {msg['role']}\n  content: |\n")
                        for line in content.splitlines():
                            f.write(f"    {line}\n")
            elif isinstance(message, dict):
                f.write("- ")
                first = True
                for key, value in message.items():
                    prefix = "  " if not first else ""
                    parsed = None
                    if isinstance(value, str):
                        try:
                            parsed = json.loads(value)
                        except json.JSONDecodeError:
                            pass
                    if isinstance(parsed, (dict, list)):
                        f.write(f"{prefix}{key}:\n")
                        for line in yaml.dump(parsed, sort_keys=False, allow_unicode=True, indent=2).splitlines():
                            f.write(f"    {line}\n")
                    elif isinstance(value, str) and "\n" in value:
                        f.write(f"{prefix}{key}: |\n")
                        for line in value.splitlines():
                            f.write(f"    {line}\n")
                    else:
                        lines = yaml.dump({key: value}, sort_keys=False, allow_unicode=True, indent=2).splitlines()
                        f.write(f"{prefix}{lines[0]}\n")
                        for line in lines[1:]:
                            f.write(f"  {line}\n")
                    first = False

