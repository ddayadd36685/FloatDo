@echo off
set "VENV_PATH=.venv"

if exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Activating virtual environment...
    call "%VENV_PATH%\Scripts\activate.bat"
) else (
    echo Warning: Virtual environment not found at %VENV_PATH%.
    echo Please ensure you are running in the correct environment.
)

echo Starting Nuitka Build...
echo This might take a while.

:: Clean previous build
if exist "dist" rmdir /s /q "dist"

:: Build Command
nuitka ^
    --standalone ^
    --enable-plugin=pyqt6 ^
    --include-data-dir=assets=assets ^
    --output-dir=dist ^
    --output-filename=TodoApp.exe ^
    --windows-console-mode=disable ^
    --company-name="MyTodoApp" ^
    --product-name="TodoApp" ^
    --file-version=1.0.0.0 ^
    --include-module=uvicorn ^
    --include-module=fastapi ^
    --show-progress ^
    --show-memory ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo Build finished successfully!
    echo Executable is located at: dist\TodoApp.dist\TodoApp.exe
) else (
    echo Build failed!
)
pause
