# AI Dev Pipeline Tool

CLI tool for managing a staged AI-assisted development workflow:

```text
spec -> test -> code
```

Each phase requires explicit human approval before the workflow can advance.

## Project Structure

```text
src/ai_dev_pipeline_tool/
    cli.py
    state.py
    workflow.py

tests/
    test_state.py
    test_workflow.py
    test_cli.py

docs/specs/
    pipeline/spec.md

workspace/current/
    state.json
```

## Package Name

The Python package name is unified as:

```text
ai_dev_pipeline_tool
```

## Expected Module APIs

The current test suite assumes the following public APIs:

```python
# state.py
initialize_state(state_path)
load_state(state_path)
save_state(state_path, state_data)

# workflow.py
approve_phase(current_state, phase_name)

# cli.py
main(argv=None)
```

## Workflow Rules

The workflow must always progress in this order:

```text
spec -> test -> code
```

Behavior for approval commands is defined as:

* `approve spec`: approves the `spec` phase and advances to `test`
* `approve tests`: approves the `test` phase and advances to `code`

Invalid transitions must be blocked.

## State File

State is stored in:

```text
workspace/current/state.json
```

Expected format:

```json
{
  "feature_name": "pipeline",
  "phase": "spec",
  "spec_approved": false,
  "tests_approved": false,
  "implementation_completed": false
}
```

## Constraints

* Keep the tool CLI-based
* Do not introduce a database
* Do not introduce a web UI
* Only write workflow state under `workspace/current/`
* Do not modify `docs/specs/pipeline/spec.md` through implementation work
