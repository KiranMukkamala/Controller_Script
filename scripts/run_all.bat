@echo off
REM ============================================================
REM SessionConf Documentation Toolchain
REM Baseline-based checksum validation enabled
REM ============================================================

REM ------------------------------------------------------------
REM Always start in script directory
REM ------------------------------------------------------------
cd /d %~dp0
echo Script directory: %CD%

REM ------------------------------------------------------------
REM Find repository root (contains inputs\sdf)
REM ------------------------------------------------------------
:find_root
if exist inputs\sdf goto root_found
cd ..
if "%CD%"=="%~dp0" goto root_error
goto find_root

:root_found
echo Repository root detected: %CD%
echo.

REM ------------------------------------------------------------
REM Python diagnostics
REM ------------------------------------------------------------
echo Python version:
python --version
echo.

echo Checking PyYAML...
python -c "import yaml; print('PyYAML version:', yaml.__version__)"
if errorlevel 1 goto yaml_error
echo.

REM ------------------------------------------------------------
REM Pipeline steps
REM ------------------------------------------------------------

echo [1/8] Extracting macros from SDF
python tools\extract_macros\extract_macros_from_sdf.py
if errorlevel 1 goto step_error

echo [2/8] Validating Events vs Macros
python tools\validate\validate_events_vs_macros.py
if errorlevel 1 goto step_error

echo [3/8] Validating GUI vs LDF
python tools\validate\validate_gui_vs_ldf.py
if errorlevel 1 goto step_error

REM ------------------------------------------------------------
REM Baseline-based checksum handling
REM ------------------------------------------------------------

echo [4/8] Computing current input checksums (SDF/LDF)
python tools\validate\compute_current_checksums.py
if errorlevel 1 goto step_error

echo [5/8] Validating against baseline checksums
python tools\validate\validate_and_update_input_checksums.py --accept
if errorlevel 1 goto step_error

REM ------------------------------------------------------------
REM HTML generation
REM ------------------------------------------------------------

echo [6/8] Generating overview HTML report
python tools\report\generate_html_report.py
if errorlevel 1 goto step_error

echo [7/8] Generating per-macro HTML pages
python tools\report\generate_macro_html.py
if errorlevel 1 goto step_error

REM ------------------------------------------------------------
REM Validation & verification
REM ------------------------------------------------------------

echo [8/8] Running macro consistency checks
python tools\validate\check_macro_consistency.py
if errorlevel 1 goto step_error

echo.
echo [CHECK] Running HTML macro link checks...
python tools\validate\check_macro_html_links.py
if errorlevel 1 goto step_error

echo.
echo [REPORT] Generating verification report...
python tools\report\generate_verification_report.py
if errorlevel 1 goto step_error

echo.
echo ALL STEPS COMPLETED SUCCESSFULLY
pause
exit /b 0

REM ------------------------------------------------------------
REM Error handlers
REM ------------------------------------------------------------
:yaml_error
echo PyYAML import failed
echo Run: python -m pip install PyYAML
pause
exit /b 1

:step_error
echo A SCRIPT FAILED — SEE ERROR ABOVE
pause
exit /b 1

:root_error
echo Could not find repository root (inputs\sdf)
pause
exit /b 1