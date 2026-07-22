#!/usr/bin/env python3
"""Cross-platform bootstrap for the Irmia DevKit MCP server."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import venv
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
VENV = ROOT / ".venv"
VENV_PYTHON = VENV / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
REQUIREMENTS = ROOT / "requirements.txt"
SERVER = ROOT / "server.py"
EXPECTED = {
    "mcp": "1.27.0",
    "beautifulsoup4": "4.15.0",
    "lxml": "6.1.1",
    "PyYAML": "6.0.3",
    "psutil": "7.2.2",
}


def _dependencies_match() -> bool:
    code = (
        "from importlib.metadata import version;"
        f"e={EXPECTED!r};"
        "raise SystemExit(0 if all(version(k)==v for k,v in e.items()) else 1)"
    )
    return subprocess.run(
        [str(VENV_PYTHON), "-c", code],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    ).returncode == 0


def _bootstrap() -> None:
    if sys.version_info < (3, 10):
        raise SystemExit("[irmia-devkit] Error: Python >= 3.10 is required.")
    if not VENV_PYTHON.is_file():
        print(f"[irmia-devkit] Creating local venv: {VENV}", file=sys.stderr)
        venv.EnvBuilder(with_pip=True).create(VENV)
    if not _dependencies_match():
        print("[irmia-devkit] Installing pinned dependencies into local venv...", file=sys.stderr)
        completed = subprocess.run(
            [str(VENV_PYTHON), "-m", "pip", "install", "--requirement", str(REQUIREMENTS), "-q"],
            stdout=sys.stderr,
            stderr=sys.stderr,
            check=False,
        )
        if completed.returncode:
            raise SystemExit("[irmia-devkit] Error: dependency install failed. Check network/pip.")


def main() -> None:
    _bootstrap()
    if shutil.which("ruff") is None:
        print("[irmia-devkit] Optional: ruff not found - lint_runner prefers it.", file=sys.stderr)
    os.execv(str(VENV_PYTHON), [str(VENV_PYTHON), str(SERVER), *sys.argv[1:]])


if __name__ == "__main__":
    main()
