import json
from pathlib import Path
from typing import Any
from app.utils.logging import get_logger


logger = get_logger("helpers")

def save_json(data: Any, filepath: str | Path) -> None:
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except (OSError, TypeError, ValueError) as e:
        logger.critical(f"Error saving JSON to {filepath}: {e}")


def load_json(filepath: str | Path) -> dict | list | None:
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.critical(f"File not found: {filepath}")
        return None
    except json.JSONDecodeError as e:
        logger.critical(f"Invalid JSON in {filepath}: {e}")
        return None