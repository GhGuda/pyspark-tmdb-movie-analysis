import json
from pathlib import Path
import logging

def save_json(data, filepath):
    try:
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        logging.critical(f"Error saving JSON to {filepath}: {e}")
        return None

def load_json(filepath):
    try:
        with open(filepath) as f:
            return json.load(f)
    except FileNotFoundError:
        logging.critical(f"File not found: {filepath}")
        return None