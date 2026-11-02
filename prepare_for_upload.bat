@echo off
echo ===================================================
echo [1/3] Copying User-Uploaded Photos to Project...
echo ===================================================

set "BRAIN=C:\Users\Shawon!\.gemini\antigravity\brain\679b3919-0a4a-45c6-bf86-b8f53d770aff"
set "SRC=%BRAIN%\.user_uploaded"
set "DEST_STATIC=%~dp0static\images\cases"
set "DEST_MEDIA=%~dp0media\case_photos"
set "DEST_STATICFILES=%~dp0staticfiles\images\cases"

mkdir "%DEST_STATIC%" 2>nul
mkdir "%DEST_MEDIA%" 2>nul
mkdir "%DEST_STATICFILES%" 2>nul
mkdir "%~dp0media\profile_photos" 2>nul
mkdir "%~dp0static\images" 2>nul
mkdir "%~dp0staticfiles\images" 2>nul

echo Copying Rayan Ahmed photo (WHERE ARE WE?)...
copy /Y "%SRC%\media_1790969660967.png" "%DEST_STATIC%\rayan_ahmed.jpg"
copy /Y "%SRC%\media_1790969660967.png" "%DEST_STATIC%\rayan_ahmed.png"
copy /Y "%SRC%\media_1790969660967.png" "%DEST_MEDIA%\rayan_ahmed.jpg"
copy /Y "%SRC%\media_1790969660967.png" "%DEST_STATICFILES%\rayan_ahmed.jpg"

echo Copying Haji Abdul Karim photo (Brown Punjabi & Cane)...
copy /Y "%SRC%\media_1790969799983.png" "%DEST_STATIC%\haji_abdul_karim.jpg"
copy /Y "%SRC%\media_1790969799983.png" "%DEST_STATIC%\haji_abdul_karim.png"
copy /Y "%SRC%\media_1790969799983.png" "%DEST_MEDIA%\haji_abdul_karim.jpg"
copy /Y "%SRC%\media_1790969799983.png" "%DEST_STATICFILES%\haji_abdul_karim.jpg"

echo Copying Nusrat Jahan & Fatema Begum photos...
copy /Y "%BRAIN%\nusrat_jahan_1790967168441.jpg" "%DEST_STATIC%\nusrat_jahan.jpg"
copy /Y "%BRAIN%\fatema_begum_1790967829834.jpg" "%DEST_STATIC%\fatema_begum.jpg"

echo ===================================================
echo [2/3] Copying Hero Banner Backgrounds...
echo ===================================================
copy /Y "%BRAIN%\aponjon_hero_dark_1791014999633.jpg" "%~dp0static\images\aponjon_hero_dark.jpg"
copy /Y "%BRAIN%\aponjon_hero_dark_1791014999633.jpg" "%~dp0staticfiles\images\aponjon_hero_dark.jpg"
copy /Y "%BRAIN%\aponjon_hero_dark_1791014999633.jpg" "%~dp0static\images\hero_family.jpg"
copy /Y "%BRAIN%\aponjon_hero_dark_1791014999633.jpg" "%~dp0staticfiles\images\hero_family.jpg"

echo.
echo ===================================================
echo [3/3] SUCCESS! All photos & hero banner copied!
echo Now zip this "Aponjon_mywebsite" folder and upload it 
echo to PythonAnywhere.
echo ===================================================
pause
