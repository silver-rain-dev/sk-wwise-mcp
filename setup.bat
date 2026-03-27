@echo off
echo.
echo SK Wwise MCP — Setup
echo.

:: Check for uv
where uv >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found uv, using it for setup...
    cd /d "%~dp0"
    uv run setup.py
    exit /b
)

:: Check for python
where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    echo Found python, using it for setup...
    cd /d "%~dp0"
    python setup.py
    exit /b
)

echo ERROR: Neither uv nor python found. Please install one of:
echo   - uv: https://docs.astral.sh/uv/getting-started/installation/
echo   - Python 3.12+: https://www.python.org/downloads/
pause
