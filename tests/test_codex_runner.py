from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

from conftest import import_project_module


def test_run_codex_calls_codex_cli_with_expected_arguments(tmp_path):
    """run_codexがcodexを対象リポジトリcwdで正しい引数実行すること"""
    codex_runner_module = import_project_module("codex_runner")
    recorded = {}

    def fake_executor(command, **kwargs):
        recorded["command"] = command
        recorded["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="generated")

    result = codex_runner_module.run_codex(
        "tests",
        tmp_path,
        "read spec and write tests",
        executor=fake_executor,
    )

    assert result == codex_runner_module.RunResult(
        task_type="tests",
        stdout="generated",
    )
    assert recorded["command"] == ["codex", "read spec and write tests"]
    assert recorded["kwargs"]["cwd"] == tmp_path
    assert recorded["kwargs"]["capture_output"] is True
    assert recorded["kwargs"]["text"] is True
    assert recorded["kwargs"]["check"] is False


def test_run_codex_raises_runtime_error_when_codex_command_is_missing(tmp_path):
    """Codex CLIが見つからない場合はRuntimeErrorになること"""
    codex_runner_module = import_project_module("codex_runner")

    def fake_executor(command, **kwargs):
        raise FileNotFoundError("codex not found")

    with pytest.raises(RuntimeError):
        codex_runner_module.run_codex(
            "tests",
            tmp_path,
            "prompt",
            executor=fake_executor,
        )


def test_run_codex_raises_runtime_error_when_codex_returns_non_zero(tmp_path):
    """Codex CLIが非0終了した場合はRuntimeErrorになること"""
    codex_runner_module = import_project_module("codex_runner")

    def fake_executor(command, **kwargs):
        return SimpleNamespace(returncode=1, stdout="", stderr="failed")

    with pytest.raises(RuntimeError):
        codex_runner_module.run_codex(
            "code",
            tmp_path,
            "prompt",
            executor=fake_executor,
        )


def test_run_result_keeps_only_minimum_success_information():
    """RunResultが成功時の最小情報だけを保持すること"""
    codex_runner_module = import_project_module("codex_runner")

    result = codex_runner_module.RunResult(task_type="tests", stdout="ok")

    assert result.task_type == "tests"
    assert result.stdout == "ok"
    assert tuple(result.__dataclass_fields__) == ("task_type", "stdout")
