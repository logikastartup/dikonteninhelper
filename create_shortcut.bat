@echo off
setlocal EnableDelayedExpansion

:: Get the directory where the batch file is located
set "SCRIPT_DIR=%~dp0"
set "SHORTCUT_PATH=%SCRIPT_DIR%DikontenIn.lnk"
set "TARGET_PATH=%SCRIPT_DIR%dikontenin.bat"
set "ICON_PATH=%SCRIPT_DIR%favicon.ico"

:: Create a temporary VBScript to create the shortcut in current directory
(
echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
echo sLinkFile = "%SHORTCUT_PATH%"
echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
echo oLink.TargetPath = "%TARGET_PATH%"
echo oLink.IconLocation = "%ICON_PATH%"
echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
echo oLink.Save
echo WScript.Echo "Shortcut created successfully"
) > "%TEMP%\CreateShortcut.vbs"

:: Execute the VBScript
cscript //nologo "%TEMP%\CreateShortcut.vbs"

:: Delete the temporary VBScript
del "%TEMP%\CreateShortcut.vbs"

echo Shortcut created successfully at: %SHORTCUT_PATH%

:: Ask user if they want to create a shortcut on the desktop
echo.
set /p DESKTOP_CHOICE="Would you like to create a shortcut on the desktop? (Y/N): "

if /i "%DESKTOP_CHOICE%"=="Y" (
    echo Creating desktop shortcut...
    
    :: Create a VBScript to make a desktop shortcut using the SpecialFolders method
    :: This method is the most reliable for finding the Desktop across different Windows versions
    (
    echo Set oWS = WScript.CreateObject^("WScript.Shell"^)
    echo strDesktop = oWS.SpecialFolders^("Desktop"^)
    echo sLinkFile = strDesktop ^& "\DikontenIn.lnk"
    echo Set oLink = oWS.CreateShortcut^(sLinkFile^)
    echo oLink.TargetPath = "%TARGET_PATH%"
    echo oLink.IconLocation = "%ICON_PATH%"
    echo oLink.WorkingDirectory = "%SCRIPT_DIR%"
    echo oLink.Save
    echo WScript.Echo "Desktop shortcut created at " ^& sLinkFile
    ) > "%TEMP%\CreateDesktopShortcut.vbs"
    
    :: Execute the VBScript
    cscript //nologo "%TEMP%\CreateDesktopShortcut.vbs"
    
    :: Delete the temporary VBScript
    del "%TEMP%\CreateDesktopShortcut.vbs"
)

endlocal
