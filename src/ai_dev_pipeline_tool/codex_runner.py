from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import subprocess
from typing import Callable


@dataclass(frozen=True)
class RunResult:
    task_type: str
    stdout: str


def _default_executor(command: list[str], **kwargs):
    return subprocess.run(command, **kwargs)


def run_codex(
    task_type: str,
    repo_path: Path,
    prompt: str,
    executor: Callable[..., object] | None = None,
) -> RunResult:
    command_executor = executor or _default_executor
    try:
        completed = command_executor(
            ["codex", prompt],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=False,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("Codex CLI is not available.") from exc

    if completed.returncode != 0:
        raise RuntimeError("Codex CLI execution failed")

    return RunResult(task_type=task_type, stdout=completed.stdout)
