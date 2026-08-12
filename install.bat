@echo off
REM Cross-platform installer for Windows.
REM Run this from the repository root.

SETLOCAL ENABLEDELAYEDEXPANSION

if exist "%~dp0install.py" (
    set SCRIPT_DIR=%~dp0
) else (
    echo Error: install.py not found in the repository root.
    exit /b 1
)

REM Prefer py launcher if available, fallback to python.
where py >nul 2>&1
if %ERRORLEVEL% == 0 (
    set PYTHON=py -3
) else (
    where python >nul 2>&1
    if %ERRORLEVEL% == 0 (
        set PYTHON=python
    ) else (
        echo Error: Python 3.9+ is required. Install Python and rerun.
        exit /b 1
    )
)

%PYTHON% "%~dp0install.py"
if %ERRORLEVEL% neq 0 (
    echo Installation failed.
    exit /b %ERRORLEVEL%
)
echo Installation complete.
