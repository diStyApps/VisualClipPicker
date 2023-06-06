@echo off

REM Activate the existing venv
call venv\Scripts\activate.bat

REM Run
python main.py

REM Deactivate the venv
call venv\Scripts\deactivate.bat

pause
