"""Repository packaging and plugin-manifest invariants."""

import hashlib
import json
import os
import re
from pathlib import Path

from tools._vendor import EXPECTED_SHA256
from tools import _vendor


ROOT = Path(__file__).resolve().parents[1]
PINNED_SHA256 = {
    "es.exe": "5101b3a6d9542de378e077f4b8c66c4e608d3bff088092427749b65fbb18b342",
    "fd": "78d315b3ed7bb8cc42052880c7be02454ad5324c7c853c291c53b0aaf6f4367b",
    "fd.exe": "4c9d082ee20f0d9e44881ac4e92adf765efc314d82103c53d7f576bd78dc5761",
    "rg": "e62198eb19b136b88c330af83647b5a962cb99b6b1f066758568f12de1974849",
    "rg.exe": "14231169855ec5205cf5a1b6f1db358ff4aed4247c86b69ce8aae647c77f6680",
}


def test_versions_are_synchronized():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    plugin = json.loads((ROOT / "reasonix-plugin.json").read_text(encoding="utf-8"))
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    project_version = re.search(r'^version = "([^"]+)"$', pyproject, re.MULTILINE)
    assert project_version is not None
    assert package["version"] == plugin["version"] == project_version.group(1)


def test_plugin_declares_existing_skill_and_launcher():
    plugin = json.loads((ROOT / "reasonix-plugin.json").read_text(encoding="utf-8"))
    skill_root = ROOT / plugin["skills"]
    assert (skill_root / "dev-workflow" / "SKILL.md").is_file()
    command = plugin["mcpServers"]["irmia-devkit"]["command"]
    launcher = ROOT / command
    assert launcher.is_file()
    if os.name != "nt":
        assert os.access(launcher, os.X_OK)


def test_npm_uses_node_launcher_instead_of_batch_shebang():
    package = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
    assert set(package["bin"].values()) == {"./bin/irmia-devkit.js"}
    launcher = ROOT / "bin" / "irmia-devkit.js"
    assert launcher.read_text(encoding="utf-8").startswith("#!/usr/bin/env node\n")
    if os.name != "nt":
        assert os.access(launcher, os.X_OK)


def test_bundled_binary_checksums_and_modes():
    sums = {}
    for line in (ROOT / "vendor" / "SHA256SUMS").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(maxsplit=1)
        sums[Path(name).name] = digest
    assert sums == EXPECTED_SHA256 == PINNED_SHA256
    for name, expected in sums.items():
        path = ROOT / "vendor" / name
        assert hashlib.sha256(path.read_bytes()).hexdigest() == expected
    if os.name != "nt":
        assert os.access(ROOT / "vendor" / "rg", os.X_OK)
        assert os.access(ROOT / "vendor" / "fd", os.X_OK)


def test_bundled_binary_fails_closed_when_checksum_entry_is_missing(tmp_path, monkeypatch):
    binary = tmp_path / "rg"
    binary.write_bytes(b"not-a-release-binary")
    binary.chmod(0o755)
    monkeypatch.setattr(_vendor, "VENDOR_DIR", tmp_path)
    monkeypatch.setattr(_vendor, "EXPECTED_SHA256", {})
    monkeypatch.setattr(_vendor, "_supported_name", lambda _tool: "rg")
    assert _vendor.bundled_executable("rg") == ""
