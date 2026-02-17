@echo off
echo Starting Nuitka Build...
echo This might take a while.

nuitka ^
    --standalone ^
    --enable-plugin=pyqt6 ^
    --include-data-dir=assets=assets ^
    --output-dir=dist ^
    --windows-console-mode=disable ^
    --company-name="MyTodoApp" ^
    --product-name="TodoApp" ^
    --file-version=1.0.0.0 ^
    main.py

echo Build finished. Check dist/main.dist/main.exe
pause
