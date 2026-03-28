from __future__ import annotations

import json

import pytest

from conftest import import_project_module


def test_initialize_state_creates_default_spec_phase_state_file(tmp_path):
    """初期化時にspecフェーズの既定状態がstate.jsonへ保存されること"""
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


def test_load_state_returns_persisted_state_when_json_is_valid(tmp_path):
    """有効なstate.jsonから保存済みの状態をそのまま読み込めること"""
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


def test_save_state_persists_updated_state_to_json_file(tmp_path):
    """状態保存時に更新済みの内容がstate.jsonへ永続化されること"""
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


def test_load_state_raises_file_not_found_when_state_json_is_missing(tmp_path):
    """state.jsonが存在しない場合は読み込み時にFileNotFoundErrorになること"""
    state_module = import_project_module("state")
    missing_path = tmp_path / "workspace" / "current" / "state.json"

    with pytest.raises(FileNotFoundError):
        state_module.load_state(missing_path)


def test_load_state_raises_value_error_when_state_json_is_broken(tmp_path):
    """壊れたJSONのstate.jsonはValueErrorとして拒否されること"""
    state_module = import_project_module("state")
    broken_path = tmp_path / "workspace" / "current" / "state.json"
    broken_path.parent.mkdir(parents=True, exist_ok=True)
    broken_path.write_text("{not-json", encoding="utf-8")

    with pytest.raises(ValueError):
        state_module.load_state(broken_path)


def test_load_state_rejects_empty_json_object_as_invalid_state(tmp_path):
    """空オブジェクトのstate.jsonは必須情報不足として拒否されること"""
    state_module = import_project_module("state")
    empty_path = tmp_path / "workspace" / "current" / "state.json"
    empty_path.parent.mkdir(parents=True, exist_ok=True)
    empty_path.write_text("{}", encoding="utf-8")

    with pytest.raises((KeyError, ValueError)):
        state_module.load_state(empty_path)


def test_load_state_rejects_missing_required_keys(tmp_path):
    """必須キーが欠損したstate.jsonは不正な状態として拒否されること"""
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
