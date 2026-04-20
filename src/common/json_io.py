from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict


def load_json_object(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("JSON file must contain an object")
    return payload


def load_string_map(path: Path) -> Dict[str, str]:
    payload = load_json_object(path)
    if isinstance(payload.get("fields"), dict):
        source = payload["fields"]
    else:
        source = payload
    return {str(key): str(value) for key, value in source.items()}


def dump_json(payload: Any) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def write_json_file(path: Path, payload: Any) -> str:
    text = dump_json(payload)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return text