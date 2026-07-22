"""Resolve bundled search executables for supported OS/architecture pairs."""

from __future__ import annotations

import hashlib
import os
import platform
from pathlib import Path


VENDOR_DIR = Path(__file__).resolve().parent.parent / "vendor"


def _load_expected_sha256() -> dict[str, str]:
    """Load the single runtime checksum manifest used by release tooling."""
    result: dict[str, str] = {}
    try:
        lines = (VENDOR_DIR / "SHA256SUMS").read_text(encoding="utf-8").splitlines()
    except OSError:
        return result
    for line in lines:
        parts = line.split()
        if len(parts) != 2 or len(parts[0]) != 64:
            return {}
        digest, raw_name = parts
        name = Path(raw_name.lstrip("*")).name
        if name in result or any(char not in "0123456789abcdefABCDEF" for char in digest):
            return {}
        result[name] = digest.casefold()
    return result


EXPECTED_SHA256 = _load_expected_sha256()


def _x86_64() -> bool:
    return platform.machine().casefold() in {"amd64", "x86_64"}


def _supported_name(tool: str) -> str | None:
    system = platform.system()
    if system == "Windows" and _x86_64():
        return {"es": "es.exe", "fd": "fd.exe", "rg": "rg.exe"}.get(tool)
    if system == "Linux" and _x86_64():
        return {"fd": "fd", "rg": "rg"}.get(tool)
    return None


def bundled_executable(tool: str) -> str:
    """Return a verified bundled executable path, or an empty string."""
    name = _supported_name(tool)
    if not name:
        return ""
    candidate = VENDOR_DIR / name
    if not candidate.is_file():
        return ""
    if os.name != "nt" and not os.access(candidate, os.X_OK):
        return ""
    digest = hashlib.sha256(candidate.read_bytes()).hexdigest()
    if digest != EXPECTED_SHA256.get(name):
        return ""
    return str(candidate)
