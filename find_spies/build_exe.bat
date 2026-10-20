@echo off
chcp 65001 >nul
echo ====================================================
echo  Сборка SpyAnalyzer.exe
echo ====================================================

echo [1/3] Проверка зависимостей...
pip install pandas numpy scipy networkx matplotlib pyinstaller

echo [2/3] Очистка предыдущих сборок...
rmdir /s /q build dist 2>nul
del SpyAnalyzer.spec 2>nul

echo [3/3] Сборка EXE файла (это займёт 2-5 минут)...
pyinstaller --noconfirm ^
    --onefile ^
    --console ^
    --name "SpyAnalyzer" ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=scipy.sparse ^
    --hidden-import=scipy.sparse.csgraph ^
    --hidden-import=networkx ^
    --hidden-import=matplotlib ^
    --hidden-import=matplotlib.pyplot ^
    main.py

echo ====================================================
echo  ГОТОВО! Файл: dist\SpyAnalyzer.exe
echo  Не забудьте положить папку datasets рядом с EXE!
echo ====================================================
pause