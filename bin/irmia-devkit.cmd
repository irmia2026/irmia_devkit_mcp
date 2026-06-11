@echo off
setlocal enabledelayedexpansion

:: ── 找 Python ──────────────────────────────────────────
set PYTHON=
for %%C in (python python3) do (
    where %%C >nul 2>nul
    if !errorlevel! equ 0 (
        set PYTHON=%%C
        goto :found_python
    )
)
echo Error: Python ^>= 3.10 not found. Install: https://python.org
exit /b 1

:found_python
:: ── 自动安装 mcp ───────────────────────────────────────
%PYTHON% -c "import mcp" 2>nul
if %errorlevel% neq 0 (
    echo [irmia-devkit] Installing mcp...
    %PYTHON% -m pip install "mcp>=1.0.0" -q
)

:: ── 检查可选依赖（不自动安装，只报告） ────────────────
where rg       >nul 2>nul || echo [irmia-devkit] Optional: rg not found - rg_search will use Python fallback. Install: winget install BurntSushi.ripgrep.MSVC
where gh       >nul 2>nul || echo [irmia-devkit] Optional: gh not found - gh_pr/gh_issue need it. Install: winget install GitHub.cli
where ruff     >nul 2>nul || echo [irmia-devkit] Optional: ruff not found - lint_runner prefers it. Install: pip install ruff
%PYTHON% -c "import bs4"        2>nul || echo [irmia-devkit] Optional: beautifulsoup4 not found - html_extract needs it. Install: pip install beautifulsoup4
%PYTHON% -c "import tree_sitter" 2>nul || echo [irmia-devkit] Optional: tree-sitter not found - code_index non-Python langs need it. Install: pip install tree-sitter

:: ── 启动 ───────────────────────────────────────────────
%PYTHON% "%~dp0..\server.py" %*
