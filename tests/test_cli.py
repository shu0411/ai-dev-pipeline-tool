from __future__ import annotations

import json
from pathlib import Path

import pytest

from conftest import import_project_module


def run_cli(cli_module, argv):
    try:
        return cli_module.main(argv)
    except TypeError:
        import sys

        original_argv = sys.argv[:]
        sys.argv = ["ai-dev-pipeline-tool", *argv]
        try:
            return cli_module.main()
        finally:
            sys.argv = original_argv


def read_state_file(root: Path) -> dict:
    return json.loads(
        (root / "workspace" / "current" / "state.json").read_text(encoding="utf-8")
    )


def test_init_command_creates_default_state_file_in_workspace(tmp_path, monkeypatch, capsys):
    """initコマンドで既定のstate.jsonがworkspace配下に作成されること"""
    cli_module = import_project_module("cli")
    monkeypatch.chdir(tmp_path)

    exit_code = run_cli(cli_module, ["init"])

    assert exit_code == 0
    assert read_state_file(tmp_path) == {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }
    captured = capsys.readouterr()
    assert "spec" in captured.out


def test_show_status_reports_current_phase_and_approval_flags(tmp_path, monkeypatch, capsys):
    """show-statusコマンドで現在フェーズと承認状態が表示されること"""
    cli_module = import_project_module("cli")
    monkeypatch.chdir(tmp_path)
    workspace_dir = tmp_path / "workspace" / "current"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "state.json").write_text(
        json.dumps(
            {
                "feature_name": "pipeline",
                "phase": "test",
                "spec_approved": True,
                "tests_approved": False,
                "implementation_completed": False,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(cli_module, ["show-status"])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert "test" in captured.out
    assert "spec_approved" in captured.out
    assert "tests_approved" in captured.out


def test_approve_spec_command_advances_persisted_state_to_test_phase(
    tmp_path, monkeypatch, capsys
):
    """approve specコマンドで保存済み状態がtestフェーズへ更新されること"""
    cli_module = import_project_module("cli")
    monkeypatch.chdir(tmp_path)
    workspace_dir = tmp_path / "workspace" / "current"
    workspace_dir.mkdir(parents=True, exist_ok=True)
    (workspace_dir / "state.json").write_text(
        json.dumps(
            {
                "feature_name": "pipeline",
                "phase": "spec",
                "spec_approved": False,
                "tests_approved": False,
                "implementation_completed": False,
            }
        ),
        encoding="utf-8",
    )

    exit_code = run_cli(cli_module, ["approve", "spec"])

    assert exit_code == 0
    assert read_state_file(tmp_path)["phase"] == "test"
    captured = capsys.readouterr()
    assert "test" in captured.out


def test_cli_rejects_approve_tests_before_initialization(tmp_path, monkeypatch):
    """初期化前にapprove testsを実行すると拒否されること"""
    cli_module = import_project_module("cli")
    monkeypatch.chdir(tmp_path)

    with pytest.raises((FileNotFoundError, SystemExit, ValueError)):
        run_cli(cli_module, ["approve", "tests"])


def test_cli_rejects_unknown_command(tmp_path, monkeypatch):
    """未定義のCLIコマンドを実行すると拒否されること"""
    cli_module = import_project_module("cli")
    monkeypatch.chdir(tmp_path)

    with pytest.raises((SystemExit, ValueError)):
        run_cli(cli_module, ["unexpected-command"])
