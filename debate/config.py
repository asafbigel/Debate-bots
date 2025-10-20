import json
import os
from typing import Any, Dict


class ConfigError(Exception):
    pass


class ConfigLoader:
    """Responsible for loading JSON configuration files.

    Single Responsibility: only load and validate configs.
    """

    def __init__(self, path: str = "config.json"):
        self.path = path

    def load(self) -> Dict[str, Any]:
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                return json.load(fh)
        except FileNotFoundError:
            raise ConfigError(f"Config file not found: {self.path}")
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {self.path}: {exc}")


class KeysLoader:
    """Responsible for loading API keys and setting environment variables.

    Uses Adapter pattern to remain testable and allow alternative key stores.
    """

    def __init__(self, path: str = "keys.json", env=os.environ):
        self.path = path
        self._env = env

    def load(self) -> None:
        try:
            with open(self.path, "r", encoding="utf-8") as fh:
                keys = json.load(fh)
        except FileNotFoundError:
            raise ConfigError(f"Keys file not found: {self.path}")
        except json.JSONDecodeError as exc:
            raise ConfigError(f"Invalid JSON in {self.path}: {exc}")

        # Map known keys into environment variables (non-invasive)
        for key_name in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY"):
            if key_name in keys:
                self._env[key_name] = keys[key_name]
