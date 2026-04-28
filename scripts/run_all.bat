@echo off
REM ============================================================
REM SessionConf Documentation Toolchain (DEBUG MODE)
REM ============================================================

REM Always start in script directory
cd /d %~dp0
echo Script directory: %CD%

REM Find repo root (folder containing inputs\sdf)
:find_root
if exist inputs\sdf goto root_found
cd ..
if "%CD%"=="%~dp0" goto root_error
goto find_root

:root_found
echo Repository root detected: %CD%
echo.

REM --- Python diagnostics ---
echo Python version:
python --version
echo.

REM --- PyYAML check ---
echo Checking PyYAML...
python -c "import yaml; print('PyYAML version:', yaml.__version__)"
if errorlevel 1 goto yaml_error
echo.

REM --- Step 1 ---
echo [1/4] Extracting macros from SDF
python tools\extract_macros\extract_macros_from_sdf.py
if errorlevel 1 goto step_error

REM --- Step 2 ---
echo [2/4] Validating Events vs Macros
python tools\validate\validate_events_vs_macros.py
if errorlevel 1 goto step_error

REM --- Step 3 ---
echo [3/4] Validating GUI vs LDF
python tools\validate\validate_gui_vs_ldf.py
if errorlevel 1 goto step_error

REM --- Step 4 ---
echo [4/4] Generating HTML report
python tools\report\generate_html_report.py
if errorlevel 1 goto step_error

echo ✅ ALL STEPS COMPLETED SUCCESSFULLY
pause
exit /b 0

:yaml_error
echo ❌ PyYAML import failed
echo Run: python -m pip install PyYAML
pause
exit /b 1

:step_error
echo ❌ A SCRIPT FAILED — SEE ERROR ABOVE
pause
exit /b 1

:root_error
echo ❌ Could not find repository root (inputs\sdf)
pause
exit /b 1