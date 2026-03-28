from __future__ import annotations

import pytest

from conftest import import_project_module


def test_approve_spec_marks_spec_approved_and_advances_to_test_phase():
    """spec承認時にspec_approvedが真となりtestフェーズへ進むこと"""
    workflow_module = import_project_module("workflow")
    current_state = {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }

    next_state = workflow_module.approve_phase(current_state, "spec")

    assert next_state["spec_approved"] is True
    assert next_state["phase"] == "test"
    assert next_state["tests_approved"] is False
    assert next_state["implementation_completed"] is False


def test_approve_tests_marks_tests_approved_and_advances_to_code_phase():
    """tests承認時にtests_approvedが真となりcodeフェーズへ進むこと"""
    workflow_module = import_project_module("workflow")
    current_state = {
        "feature_name": "pipeline",
        "phase": "test",
        "spec_approved": True,
        "tests_approved": False,
        "implementation_completed": False,
    }

    next_state = workflow_module.approve_phase(current_state, "tests")

    assert next_state["spec_approved"] is True
    assert next_state["tests_approved"] is True
    assert next_state["phase"] == "code"
    assert next_state["implementation_completed"] is False


def test_approve_tests_is_blocked_until_spec_has_been_approved():
    """specが未承認の場合はtests承認が拒否されること"""
    workflow_module = import_project_module("workflow")
    current_state = {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }

    with pytest.raises(ValueError):
        workflow_module.approve_phase(current_state, "tests")


def test_approve_phase_rejects_unknown_phase_name():
    """定義外のフェーズ名を承認対象にすると拒否されること"""
    workflow_module = import_project_module("workflow")
    current_state = {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }

    with pytest.raises(ValueError):
        workflow_module.approve_phase(current_state, "deploy")


def test_approve_phase_rejects_reapproving_an_already_approved_phase():
    """すでに通過済みのフェーズを再承認しようとすると拒否されること"""
    workflow_module = import_project_module("workflow")
    current_state = {
        "feature_name": "pipeline",
        "phase": "test",
        "spec_approved": True,
        "tests_approved": False,
        "implementation_completed": False,
    }

    with pytest.raises(ValueError):
        workflow_module.approve_phase(current_state, "spec")


def test_approve_phase_rejects_skipping_directly_from_spec_to_code():
    """specからcodeへのフェーズスキップ承認が拒否されること"""
    workflow_module = import_project_module("workflow")
    current_state = {
        "feature_name": "pipeline",
        "phase": "spec",
        "spec_approved": False,
        "tests_approved": False,
        "implementation_completed": False,
    }

    with pytest.raises(ValueError):
        workflow_module.approve_phase(current_state, "code")
