from __future__ import annotations

import json
import sys
from pathlib import Path

from .state import initialize_state, load_state, save_state
from .workflow import approve_phase

STATE_PATH = Path("workspace") / "current" / "state.json"


def _format_status(state: dict) -> str:
    return json.dumps(state, indent=2)


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        raise ValueError("A command is required.")

    command = args[0]

    if command == "init":
        state = initialize_state(STATE_PATH)
        print(_format_status(state))
        return 0

    if command == "show-status":
        state = load_state(STATE_PATH)
        print(_format_status(state))
        return 0

    if command == "approve":
        if len(args) != 2:
            raise ValueError("approve requires exactly one phase name.")
        state = load_state(STATE_PATH)
        updated_state = approve_phase(state, args[1])
        save_state(STATE_PATH, updated_state)
        print(_format_status(updated_state))
        return 0

    raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
