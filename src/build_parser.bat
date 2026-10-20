@echo off
chcp 65001 >nul
echo ====================================================
echo  Сборка DataParser.exe
echo ====================================================

echo [1/3] Установка зависимостей...
pip install pandas numpy openpyxl PyYAML pymupdf pyinstaller

echo [2/3] Очистка предыдущих сборок...
rmdir /s /q build dist 2>nul
del DataParser.spec 2>nul

echo [3/3] Сборка EXE файла (это займёт 2-5 минут)...
pyinstaller --noconfirm ^
    --onefile ^
    --console ^
    --name "DataParser" ^
    --hidden-import=pandas ^
    --hidden-import=numpy ^
    --hidden-import=openpyxl ^
    --hidden-import=yaml ^
    --hidden-import=pymupdf ^
    --hidden-import=konon_parser ^
    --hidden-import=konon_parser.xml_parser ^
    --hidden-import=konon_parser.pdf_parser ^
    --collect-all konon_parser ^
    main_parser.py

echo.
echo ====================================================
echo  ГОТОВО!
echo  EXE файл: dist\DataParser.exe
echo ====================================================
echo.
echo ВАЖНО: Создайте папку 'input_data' рядом с EXE и поместите туда:
echo   - BoardingData.csv
echo   - Sirena-export-fixed.tab
echo   - FrequentFlyerForum-Profiles.json
echo   - SkyTeam-Exchange.yaml
echo   - YourBoardingPassDotAero/ (папка с Excel)
echo   - PointzAggregator-AirlinesData.xml
echo   - Skyteam_Timetable.pdf
echo ====================================================
pause