from __future__ import annotations

import pytest

from conftest import import_project_module


def test_spec承認時にspec_approvedが真となりtestフェーズへ進むこと():
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


def test_tests承認時にtests_approvedが真となりcodeフェーズへ進むこと():
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


def test_specが未承認の場合はtests承認が拒否されること():
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


def test_定義外のフェーズ名を承認対象にすると拒否されること():
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


def test_すでに通過済みのフェーズを再承認しようとすると拒否されること():
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


def test_specからcodeへのフェーズスキップ承認が拒否されること():
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
