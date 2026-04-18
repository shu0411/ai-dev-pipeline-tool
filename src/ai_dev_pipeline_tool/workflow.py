from __future__ import annotations

VALID_PHASES = ("spec", "test", "code")


def approve_phase(current_state: dict, phase_name: str) -> dict:
    if phase_name not in {"spec", "tests"}:
        raise ValueError(f"Unsupported phase approval: {phase_name}")

    state = dict(current_state)

    if phase_name == "spec":
        if state.get("phase") != "spec":
            raise ValueError("spec can only be approved from the spec phase.")
        if state.get("spec_approved"):
            raise ValueError("spec has already been approved.")
        state["spec_approved"] = True
        state["phase"] = "test"
        return state

    if state.get("spec_approved") is not True:
        raise ValueError("tests cannot be approved before spec approval.")
    if state.get("phase") != "test":
        raise ValueError("tests can only be approved from the test phase.")
    if state.get("tests_approved"):
        raise ValueError("tests have already been approved.")

    state["tests_approved"] = True
    state["phase"] = "code"
    return state
