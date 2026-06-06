from pathlib import Path
from typing import Any

import yaml

_PROMPTS_DIR = Path(__file__).parent


def load_prompt(name: str) -> dict[str, Any]:
    """Load a prompt YAML by name (without extension)."""
    path = _PROMPTS_DIR / f"{name}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Prompt file not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_system_prompt(name: str) -> str:
    """Extract a simple system prompt string from a prompt YAML."""
    data = load_prompt(name)
    # If there is an explicit 'system' field, use it
    if "system" in data:
        return data["system"]
    # Otherwise build from purpose + rules
    parts = [f"Purpose: {data.get('purpose', '')}"]
    if "rules" in data:
        parts.append("Rules:")
        for rule in data["rules"]:
            parts.append(f"- {rule}")
    if "output_schema" in data:
        parts.append(f"Output schema: {data['output_schema']}")
    return "\n".join(parts)
