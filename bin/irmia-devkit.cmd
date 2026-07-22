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
%PYTHON% "%~dp0irmia-devkit.py" %*
exit /b %errorlevel%
