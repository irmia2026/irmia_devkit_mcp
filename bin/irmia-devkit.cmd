#!/bin/sh
# 2>NUL & @goto windows
exec "$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)/irmia-devkit.sh" "$@"
exit $?

:windows
@echo off
setlocal enabledelayedexpansion

rem -- find Python: py launcher first, then python / python3; require >= 3.10 --
set "PYTHON="
for %%C in (py python python3) do (
    where %%C >nul 2>nul
    if not errorlevel 1 (
        %%C -c "import sys;raise SystemExit(0 if sys.version_info>=(3,10) else 1)" >nul 2>nul
        if not errorlevel 1 (
            set "PYTHON=%%C"
            goto :found_python
        )
    )
)
>&2 echo [irmia-devkit] Error: Python ^>= 3.10 not found. Install: https://python.org
exit /b 1

:found_python
rem -- project-local venv (keeps global site-packages clean) --
set "VENV=%~dp0..\.venv"
set "VENV_PY=%VENV%\Scripts\python.exe"

if not exist "%VENV_PY%" (
    >&2 echo [irmia-devkit] Creating local venv: %VENV%
    %PYTHON% -m venv "%VENV%" >&2
    if errorlevel 1 (
        >&2 echo [irmia-devkit] Error: failed to create venv.
        exit /b 1
    )
)

rem -- install pinned deps into venv; pip output to stderr, stdout stays JSON-RPC only --
set "REQ=%~dp0..\requirements.txt"
"%VENV_PY%" -c "import mcp,bs4,lxml,yaml,psutil;from importlib.metadata import version;e={'mcp':'1.27.0','beautifulsoup4':'4.15.0','lxml':'6.1.1','PyYAML':'6.0.3','psutil':'7.2.2'};raise SystemExit(0 if all(version(k)==v for k,v in e.items()) else 1)" >nul 2>nul
if errorlevel 1 (
    >&2 echo [irmia-devkit] Installing dependencies into local venv...
    "%VENV_PY%" -m pip install --requirement "%REQ%" -q >&2
    if errorlevel 1 (
        >&2 echo [irmia-devkit] Error: dependency install failed. Check network/pip.
        exit /b 1
    )
)

rem -- optional tools: report only, all to stderr --
where rg >nul 2>nul || >&2 echo [irmia-devkit] Optional: rg not found - rg_search falls back to Python. Install: winget install BurntSushi.ripgrep.MSVC
where gh >nul 2>nul || >&2 echo [irmia-devkit] Optional: gh not found - gh_pr/gh_issue need it. Install: winget install GitHub.cli
where ruff >nul 2>nul || >&2 echo [irmia-devkit] Optional: ruff not found - lint_runner prefers it. Install: pip install ruff
"%VENV_PY%" -c "import tree_sitter" >nul 2>nul || >&2 echo [irmia-devkit] Optional: tree-sitter not found - code_index for non-Python langs needs it. Install: pip install tree-sitter

rem -- launch --
"%VENV_PY%" "%~dp0..\server.py" %*
