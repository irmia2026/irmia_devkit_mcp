"""Runtime executable resolution honors explicit user configuration."""

from tools import config, es_search, rg_search


def test_rg_configured_path_precedes_bundle_and_path(tmp_path, monkeypatch):
    custom = tmp_path / "my-rg"
    custom.write_text("custom", encoding="utf-8")
    config.set_config({"rg_path": str(custom)})
    monkeypatch.setattr(rg_search, "bundled_executable", lambda _tool: "/bundle/rg")
    monkeypatch.setattr(rg_search.shutil, "which", lambda _name: "/path/rg")
    assert rg_search._find_rg() == str(custom)


def test_es_configured_path_precedes_bundle_and_path(tmp_path, monkeypatch):
    custom = tmp_path / "my-es"
    custom.write_text("custom", encoding="utf-8")
    config.set_config({"es_path": str(custom)})
    monkeypatch.setattr(es_search, "bundled_executable", lambda _tool: "/bundle/es")
    monkeypatch.setattr(es_search.shutil, "which", lambda _name: "/path/es")
    assert es_search._get_es_path() == str(custom)


def test_fd_configured_path_precedes_bundle_and_path(tmp_path, monkeypatch):
    custom = tmp_path / "my-fd"
    custom.write_text("custom", encoding="utf-8")
    config.set_config({"fd_path": str(custom)})
    monkeypatch.setattr(es_search, "bundled_executable", lambda _tool: "/bundle/fd")
    monkeypatch.setattr(es_search.shutil, "which", lambda _name: "/path/fd")
    assert es_search._find_fd() == str(custom)
