from __future__ import annotations

import json

import pytest

from conftest import import_project_module


def test_初期化時にspecフェーズの既定状態がstate_jsonへ保存されること(tmp_path):
    state_module = import_project_module("state")
    state_path = tmp_path / "workspace" / "current" / "state.json"

    created_state = state_module.initialize_state(state_path)

    assert state_path.exists()
    assert created_state == {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }
    assert json.loads(state_path.read_text(encoding="utf-8")) == created_state


def test_有効なstate_jsonから保存済みの状態をそのまま読み込めること(tmp_path):
    state_module = import_project_module("state")
    state_path = tmp_path / "state.json"
    persisted_state = {
        "feature_name": "pipeline",
        "phase": "test",
        "spec_approved": True,
        "tests_approved": False,
        "implementation_completed": False,
    }
    state_path.write_text(json.dumps(persisted_state), encoding="utf-8")

    loaded_state = state_module.load_state(state_path)

    assert loaded_state == persisted_state


def test_状態保存時に更新済みの内容がstate_jsonへ永続化されること(tmp_path):
    state_module = import_project_module("state")
    state_path = tmp_path / "workspace" / "current" / "state.json"
    state_to_save = {
        "feature_name": "pipeline",
        "phase": "code",
        "spec_approved": True,
        "tests_approved": True,
        "implementation_completed": False,
    }

    state_module.save_state(state_path, state_to_save)

    assert json.loads(state_path.read_text(encoding="utf-8")) == state_to_save


def test_state_jsonが存在しない場合は読み込み時にFileNotFoundErrorになること(tmp_path):
    state_module = import_project_module("state")
    missing_path = tmp_path / "workspace" / "current" / "state.json"

    with pytest.raises(FileNotFoundError):
        state_module.load_state(missing_path)


def test_壊れたJSONのstate_jsonはValueErrorとして拒否されること(tmp_path):
    state_module = import_project_module("state")
    broken_path = tmp_path / "workspace" / "current" / "state.json"
    broken_path.parent.mkdir(parents=True, exist_ok=True)
    broken_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError):
        state_module.load_state(broken_path)


def test_空オブジェクトのstate_jsonは必須情報不足として拒否されること(tmp_path):
    state_module = import_project_module("state")
    empty_path = tmp_path / "workspace" / "current" / "state.json"
    empty_path.parent.mkdir(parents=True, exist_ok=True)
    empty_path.write_text("{}", encoding="utf-8")

    with pytest.raises((KeyError, ValueError)):
        state_module.load_state(empty_path)


def test_必須キーが欠損したstate_jsonは不正な状態として拒否されること(tmp_path):
    state_module = import_project_module("state")
    missing_key_path = tmp_path / "workspace" / "current" / "state.json"
    missing_key_path.parent.mkdir(parents=True, exist_ok=True)
    missing_key_path.write_text(
        json.dumps(
            {
                "feature_name": "pipeline",
                "phase": "spec",
                "spec_approved": False,
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises((KeyError, ValueError)):
        state_module.load_state(missing_key_path)
