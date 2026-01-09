@echo off
python run_tests %*
if ERRORLEVEL 1 exit /b 1
