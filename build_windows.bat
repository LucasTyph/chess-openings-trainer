@echo off
REM Build the Chess Opening Trainer as a standalone Windows executable
pyinstaller --noconfirm --onefile --windowed --name ChessOpeningTrainer main.py
REM Output will be in the dist/ folder
pause
