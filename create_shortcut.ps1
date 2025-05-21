$WshShell = New-Object -ComObject WScript.Shell

# Use the script's location to find the correct path
$scriptPath = Split-Path -Parent -Path $MyInvocation.MyCommand.Definition
$shortcutPath = Join-Path $scriptPath "DikontenIn.lnk"
$targetPath = Join-Path $scriptPath "dikontenin.bat"
$iconPath = Join-Path $scriptPath "favicon.ico"

$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.IconLocation = $iconPath
$Shortcut.WorkingDirectory = $scriptPath
$Shortcut.Save()

Write-Host "Shortcut created successfully at: $shortcutPath"
