from __future__ import annotations

import json
import sys
from pathlib import Path

from .codex_runner import run_codex
from .prompt_builder import build_prompt
from .state import initialize_state, load_state, save_state
from .workflow import approve_phase

STATE_DIRNAME = ".ai-dev-pipeline"
STATE_FILENAME = "state.json"


def _format_status(state: dict) -> str:
    return json.dumps(state, indent=2)


def _extract_option(args: list[str], option_name: str) -> str:
    if option_name not in args:
        raise ValueError(f"{option_name} is required.")
    option_index = args.index(option_name)
    if option_index + 1 >= len(args):
        raise ValueError(f"{option_name} requires a value.")
    return args[option_index + 1]


def _resolve_repo_path(repo_value: str) -> Path:
    repo_path = Path(repo_value).expanduser().resolve()
    if not repo_path.exists():
        raise FileNotFoundError(f"Repository path does not exist: {repo_path}")
    return repo_path


def _require_git_repo(repo_path: Path) -> None:
    if not (repo_path / ".git").exists():
        raise ValueError(f"Target repository is not a Git repository: {repo_path}")


def _state_path_for_repo(repo_path: Path) -> Path:
    return repo_path / STATE_DIRNAME / STATE_FILENAME


def _to_relative_spec_path(repo_path: Path, spec_value: str) -> str:
    spec_path = Path(spec_value)
    if spec_path.is_absolute():
        return str(spec_path.resolve().relative_to(repo_path)).replace("\\", "/")
    return spec_path.as_posix()


def _load_repo_state(repo_path: Path) -> dict:
    return load_state(_state_path_for_repo(repo_path))


def _ensure_task_allowed(state: dict, task_type: str) -> None:
    if task_type == "tests":
        if state.get("spec_approved") is not True:
            raise ValueError("spec approval is required before running tests.")
        return
    if task_type == "code":
        if state.get("tests_approved") is not True:
            raise ValueError("tests approval is required before running code.")
        return
    raise ValueError(f"Unsupported run task: {task_type}")


def _resolve_spec_file(repo_path: Path, state: dict) -> Path:
    spec_path = state.get("spec_path")
    if not spec_path:
        raise ValueError("spec_path is required in the state file.")
    resolved = repo_path / spec_path
    if not resolved.exists():
        raise FileNotFoundError(f"Spec file does not exist: {resolved}")
    return resolved


def _command_init(args: list[str]) -> int:
    repo_path = _resolve_repo_path(_extract_option(args, "--repo"))
    _require_git_repo(repo_path)
    feature_name = _extract_option(args, "--feature")
    spec_path = _to_relative_spec_path(repo_path, _extract_option(args, "--spec"))
    state = initialize_state(
        _state_path_for_repo(repo_path),
        feature_name=feature_name,
        spec_path=spec_path,
    )
    print(_format_status(state))
    return 0


def _command_show_status(args: list[str]) -> int:
    repo_path = _resolve_repo_path(_extract_option(args, "--repo"))
    state = _load_repo_state(repo_path)
    print(_format_status(state))
    return 0


def _command_approve(args: list[str]) -> int:
    if len(args) < 3:
        raise ValueError("approve requires a phase name and --repo.")
    phase_name = args[1]
    repo_path = _resolve_repo_path(_extract_option(args, "--repo"))
    state = _load_repo_state(repo_path)
    updated_state = approve_phase(state, phase_name)
    save_state(_state_path_for_repo(repo_path), updated_state)
    print(_format_status(updated_state))
    return 0


def _command_run(args: list[str]) -> int:
    if len(args) < 3:
        raise ValueError("run requires a task name and --repo.")
    task_type = args[1]
    repo_path = _resolve_repo_path(_extract_option(args, "--repo"))
    state = _load_repo_state(repo_path)
    _ensure_task_allowed(state, task_type)
    _resolve_spec_file(repo_path, state)
    prompt = build_prompt(task_type, state["spec_path"])
    result = run_codex(task_type, repo_path, prompt)
    print(result.stdout)
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        raise ValueError("A command is required.")

    command = args[0]
    if command == "init":
        return _command_init(args)
    if command == "show-status":
        return _command_show_status(args)
    if command == "approve":
        return _command_approve(args)
    if command == "run":
        return _command_run(args)
    raise ValueError(f"Unknown command: {command}")


if __name__ == "__main__":
    raise SystemExit(main())
