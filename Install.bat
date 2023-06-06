@echo off

REM 1. Create a venv folder
echo Creating venv folder...
python -m venv venv

REM 2. Activate the venv
echo Activating venv...
call venv\Scripts\activate.bat

REM 3. Install dependencies from requirements.txt
echo Installing dependencies from requirements
pip install -r requirements.txt


REM 7. Run Visual Clip Picker
echo Launching Visual Clip Picker
python main.py

pause
