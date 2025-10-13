"""Persistence utilities for reading and writing JSON data files."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    """Load JSON data from ``path``.

    The function ensures the parent directory exists and creates an empty JSON
    object if the file is missing. This keeps the rest of the application logic
    simple while allowing the data directory to be cleaned safely.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text("{}", encoding="utf-8")
    with path.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def save_json(path: Path, data: Any) -> None:
    """Write JSON ``data`` to ``path`` with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, sort_keys=True)
