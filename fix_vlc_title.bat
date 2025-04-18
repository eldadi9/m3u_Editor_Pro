@echo off
setlocal EnableDelayedExpansion

:: Path to VLC config file
set "VLC_CFG=%APPDATA%\vlc\vlcrc"
set "VLC_BAK=%APPDATA%\vlc\vlcrc.bak"

:: Backup original
copy "%VLC_CFG%" "%VLC_BAK%" >nul

:: Temp output file
set "TMP=%TEMP%\vlc_temp.txt"
if exist "%TMP%" del "%TMP%"

echo Updating VLC settings to display EXTINF titles instead of index.m3u8...

:: Read and update lines
for /f "usebackq tokens=* delims=" %%A in ("%VLC_CFG%") do (
    set "line=%%A"
    echo !line! | findstr /C:"#meta-title=yes" >nul
    if !errorlevel! == 0 (
        echo meta-title=no>>"%TMP%"
    ) else (
        echo !line!>>"%TMP%"
    )
)

:: Replace original file
move /Y "%TMP%" "%VLC_CFG%" >nul

echo Done. ✅ Please restart VLC and reload your M3U.
pause
