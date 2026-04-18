from __future__ import annotations

import json
from pathlib import Path

REQUIRED_KEYS = {
    "feature_name",
    "phase",
    "spec_approved",
    "tests_approved",
    "implementation_completed",
}


def default_state() -> dict:
    return {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }


def _validate_state(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("State data must be a JSON object.")

    missing_keys = REQUIRED_KEYS.difference(data)
    if missing_keys:
        raise KeyError(f"Missing required state keys: {sorted(missing_keys)}")

    return data


def initialize_state(state_path: str | Path) -> dict:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = default_state()
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state


def load_state(state_path: str | Path) -> dict:
    path = Path(state_path)
    raw_text = path.read_text(encoding="utf-8")
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("State file is not valid JSON.") from exc
    return _validate_state(data)


def save_state(state_path: str | Path, state_data: dict) -> dict:
    path = Path(state_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = _validate_state(state_data)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    return state
