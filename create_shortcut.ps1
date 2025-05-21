$WshShell = New-Object -ComObject WScript.Shell
$currentDir = Get-Location
$shortcutPath = Join-Path $currentDir "DikontenIn.lnk"
$targetPath = Join-Path $currentDir "dikontenin.bat"
$iconPath = Join-Path $currentDir "favicon.ico"

$Shortcut = $WshShell.CreateShortcut($shortcutPath)
$Shortcut.TargetPath = $targetPath
$Shortcut.IconLocation = $iconPath
$Shortcut.WorkingDirectory = $currentDir.Path
$Shortcut.Save()

Write-Host "Shortcut created successfully at: $shortcutPath"
