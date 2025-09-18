@echo off
echo Starting Spec Matcher...
cd /d "%~dp0"
if exist "SpecMatcher.exe" (
    start "" "SpecMatcher.exe"
) else (
    echo SpecMatcher.exe not found!
    echo Please run build_exe.py first to create the executable.
    pause
)
