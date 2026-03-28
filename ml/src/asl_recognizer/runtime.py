from __future__ import annotations

import os
from pathlib import Path


def configure_runtime_dirs() -> None:
    runtime_root = Path.cwd() / ".runtime"
    runtime_root.mkdir(parents=True, exist_ok=True)

    matplotlib_dir = runtime_root / "matplotlib"
    matplotlib_dir.mkdir(parents=True, exist_ok=True)
    os.environ.setdefault("MPLCONFIGDIR", str(matplotlib_dir.resolve()))
