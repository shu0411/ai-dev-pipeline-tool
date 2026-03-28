from __future__ import annotations

import importlib
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))


def import_project_module(module_name: str):
    """Import a project module from the unified package name."""
    return importlib.import_module(f"ai_dev_pipeline_tool.{module_name}")
