# AGENTS.md

## 1. Project Overview

This repository contains a CLI tool for managing a staged AI-assisted development workflow:

```
spec → test → code
```

Each phase must be explicitly approved by a human before proceeding.

The goal is to enforce structured development using AI while preventing uncontrolled execution.

---

## 2. Tech Stack

* Python 3.11+
* pytest
* CLI (standard library only)
* File-based state management (JSON)

---

## 3. Project Structure

```
src/ai_dev_pipeline_tool/
    cli.py
    state.py
    workflow.py

tests/
    test_state.py
    test_workflow.py

docs/specs/
    pipeline/spec.md

workspace/current/
    state.json
```

---

## 4. Core Concepts

### Phases

```
spec → test → code
```

### State

Stored in:

```
workspace/current/state.json
```

Example:

```
{
  "feature_name": "pipeline",
  "phase": "spec",
  "spec_approved": false,
  "tests_approved": false,
  "implementation_completed": false
}
```

---

## 5. Rules (VERY IMPORTANT)

### Workflow Rules

* DO NOT proceed to the next phase unless approved
* DO NOT skip phases
* ALWAYS enforce:

  spec → test → code

### Implementation Rules

* Do NOT introduce a database
* Do NOT introduce a web UI
* Keep everything CLI-based
* Use only minimal dependencies

### File Rules

* Do NOT modify files under:

  ```
  docs/specs/
  ```

* Only write state to:

  ```
  workspace/current/
  ```

* Do NOT create unnecessary files

### Behavior Rules

* If requirements are unclear, ASK instead of guessing
* Prefer minimal, incremental changes
* Keep functions small and focused

---

## 6. Testing Rules

* Use pytest
* Cover:

  * normal cases
  * invalid transitions
  * edge cases (missing state, broken JSON)
* Tests should clearly express intent in names

---

## 7. Task Execution Guidelines

When implementing:

1. Read spec:

   ```
    docs/specs/pipeline/spec.md
   ```

2. Understand current state logic

3. Implement only what is required

4. Run tests

5. Ensure no unintended changes

---

## 8. Definition of Done

### For Tests

* Tests reflect spec behavior
* Include normal + error cases
* Do NOT modify implementation yet

### For Implementation

* All tests pass
* No spec violations
* No unnecessary features added
* Code is simple and readable

---

## 9. When in doubt

* Follow the spec strictly
* Do NOT assume missing requirements
* Report unclear points explicitly
