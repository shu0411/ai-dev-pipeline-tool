from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

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


def read_target_state_file(target_repo: Path) -> dict:
    state_path = target_repo / ".ai-dev-pipeline" / "state.json"
    return json.loads(state_path.read_text(encoding="utf-8"))


def write_target_state_file(target_repo: Path, state: dict) -> None:
    state_path = target_repo / ".ai-dev-pipeline" / "state.json"
    state_path.parent.mkdir(parents=True, exist_ok=True)
    state_path.write_text(json.dumps(state), encoding="utf-8")


def make_git_repo(target_repo: Path) -> None:
    (target_repo / ".git").mkdir(parents=True, exist_ok=True)


def test_init_command_creates_state_file_in_target_repo(tmp_path, capsys):
    """initで対象リポジトリ配下に状態ファイルを作成できること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()
    make_git_repo(target_repo)

    exit_code = run_cli(
        cli_module,
        [
            "init",
            "--repo",
            str(target_repo),
            "--feature",
            "todo-app",
            "--spec",
            "docs/specs/todo-app/spec.md",
        ],
    )

    assert exit_code == 0
    assert read_target_state_file(target_repo) == {
        "feature_name": "todo-app",
        "spec_path": "docs/specs/todo-app/spec.md",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }
    assert "todo-app" in capsys.readouterr().out


def test_init_command_saves_spec_path_as_relative_when_absolute_path_is_given(tmp_path):
    """initでspec絶対パスを受け取ってもstate.jsonには相対パスで保存されること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    spec_file = target_repo / "docs" / "specs" / "todo-app" / "spec.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text("# spec", encoding="utf-8")
    make_git_repo(target_repo)

    exit_code = run_cli(
        cli_module,
        [
            "init",
            "--repo",
            str(target_repo.resolve()),
            "--feature",
            "todo-app",
            "--spec",
            str(spec_file.resolve()),
        ],
    )

    assert exit_code == 0
    assert read_target_state_file(target_repo)["spec_path"] == "docs/specs/todo-app/spec.md"


def test_init_command_rejects_non_git_target_repo(tmp_path):
    """Gitリポジトリでない対象パスをinitするとエラーになること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()

    with pytest.raises((SystemExit, ValueError)):
        run_cli(
            cli_module,
            [
                "init",
                "--repo",
                str(target_repo),
                "--feature",
                "todo-app",
                "--spec",
                "docs/specs/todo-app/spec.md",
            ],
        )


def test_show_status_reads_state_from_target_repo(tmp_path, capsys):
    """show-statusが対象リポジトリ内のstate.jsonを表示できること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()
    write_target_state_file(
        target_repo,
        {
            "feature_name": "todo-app",
            "spec_path": "docs/specs/todo-app/spec.md",
            "phase": "test",
            "spec_approved": True,
            "tests_approved": False,
            "implementation_completed": False,
        },
    )

    exit_code = run_cli(cli_module, ["show-status", "--repo", str(target_repo)])

    captured = capsys.readouterr()
    assert exit_code == 0
    assert '"phase": "test"' in captured.out
    assert "docs/specs/todo-app/spec.md" in captured.out


def test_approve_spec_updates_target_repo_state_file(tmp_path):
    """approve specが対象リポジトリ内のphaseをtestへ更新すること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()
    write_target_state_file(
        target_repo,
        {
            "feature_name": "todo-app",
            "spec_path": "docs/specs/todo-app/spec.md",
            "phase": "spec",
            "spec_approved": False,
            "tests_approved": False,
            "implementation_completed": False,
        },
    )

    exit_code = run_cli(cli_module, ["approve", "spec", "--repo", str(target_repo)])

    assert exit_code == 0
    assert read_target_state_file(target_repo)["phase"] == "test"


def test_run_tests_is_blocked_until_spec_is_approved(tmp_path):
    """spec未承認の状態ではrun testsを実行できないこと"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()
    write_target_state_file(
        target_repo,
        {
            "feature_name": "todo-app",
            "spec_path": "docs/specs/todo-app/spec.md",
            "phase": "spec",
            "spec_approved": False,
            "tests_approved": False,
            "implementation_completed": False,
        },
    )

    with pytest.raises((SystemExit, ValueError)):
        run_cli(cli_module, ["run", "tests", "--repo", str(target_repo)])


def test_run_code_is_blocked_until_tests_are_approved(tmp_path):
    """tests未承認の状態ではrun codeを実行できないこと"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()
    write_target_state_file(
        target_repo,
        {
            "feature_name": "todo-app",
            "spec_path": "docs/specs/todo-app/spec.md",
            "phase": "test",
            "spec_approved": True,
            "tests_approved": False,
            "implementation_completed": False,
        },
    )

    with pytest.raises((SystemExit, ValueError)):
        run_cli(cli_module, ["run", "code", "--repo", str(target_repo)])


def test_run_tests_rejects_missing_spec_file_before_calling_codex(tmp_path):
    """specファイルが存在しない場合はCodex実行前にエラーになること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()
    write_target_state_file(
        target_repo,
        {
            "feature_name": "todo-app",
            "spec_path": "docs/specs/todo-app/spec.md",
            "phase": "test",
            "spec_approved": True,
            "tests_approved": False,
            "implementation_completed": False,
        },
    )

    with pytest.raises((FileNotFoundError, SystemExit, ValueError)):
        run_cli(cli_module, ["run", "tests", "--repo", str(target_repo)])


def test_run_tests_does_not_update_state_after_successful_execution(tmp_path, monkeypatch):
    """run tests成功後もstate.jsonのフェーズ情報は更新されないこと"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    spec_file = target_repo / "docs" / "specs" / "todo-app" / "spec.md"
    spec_file.parent.mkdir(parents=True, exist_ok=True)
    spec_file.write_text("# spec", encoding="utf-8")
    target_repo.mkdir(exist_ok=True)
    write_target_state_file(
        target_repo,
        {
            "feature_name": "todo-app",
            "spec_path": "docs/specs/todo-app/spec.md",
            "phase": "test",
            "spec_approved": True,
            "tests_approved": False,
            "implementation_completed": False,
        },
    )

    monkeypatch.setattr(
        cli_module,
        "build_prompt",
        lambda task_type, spec_path: f"{task_type}:{spec_path}",
        raising=False,
    )
    monkeypatch.setattr(
        cli_module,
        "run_codex",
        lambda task_type, repo_path, prompt: SimpleNamespace(
            task_type=task_type,
            stdout="generated",
        ),
        raising=False,
    )

    exit_code = run_cli(cli_module, ["run", "tests", "--repo", str(target_repo)])

    assert exit_code == 0
    assert read_target_state_file(target_repo) == {
        "feature_name": "todo-app",
        "spec_path": "docs/specs/todo-app/spec.md",
        "phase": "test",
        "spec_approved": True,
        "tests_approved": False,
        "implementation_completed": False,
    }


def test_show_status_fails_before_target_repo_is_initialized(tmp_path):
    """初期化前の対象リポジトリでshow-statusを実行するとエラーになること"""
    cli_module = import_project_module("cli")
    target_repo = tmp_path / "target-app"
    target_repo.mkdir()

    with pytest.raises((FileNotFoundError, SystemExit, ValueError)):
        run_cli(cli_module, ["show-status", "--repo", str(target_repo)])
