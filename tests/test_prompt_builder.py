from __future__ import annotations

import pytest

from conftest import import_project_module


def test_tests用プロンプトが仕様で求められた指示を含むこと():
    prompt_builder_module = import_project_module("prompt_builder")

    prompt = prompt_builder_module.build_prompt(
        "tests",
        "docs/specs/todo-app/spec.md",
    )

    assert "docs/specs/todo-app/spec.md" in prompt
    assert "spec" in prompt
    assert "テスト" in prompt
    assert "pytest" in prompt
    assert "正常系" in prompt
    assert "異常系" in prompt
    assert "境界値" in prompt
    assert "実装コードは変更しない" in prompt
    assert "不明点" in prompt


def test_code用プロンプトが仕様で求められた指示を含むこと():
    prompt_builder_module = import_project_module("prompt_builder")

    prompt = prompt_builder_module.build_prompt(
        "code",
        "docs/specs/todo-app/spec.md",
    )

    assert "docs/specs/todo-app/spec.md" in prompt
    assert "spec" in prompt
    assert "既存テスト" in prompt
    assert "実装のみ" in prompt
    assert "テストを通す" in prompt
    assert "仕様外変更をしない" in prompt
    assert "不明点" in prompt


def test_未対応のtask_typeをbuild_promptに渡すとエラーになること():
    prompt_builder_module = import_project_module("prompt_builder")

    with pytest.raises(ValueError):
        prompt_builder_module.build_prompt("deploy", "docs/specs/todo-app/spec.md")
