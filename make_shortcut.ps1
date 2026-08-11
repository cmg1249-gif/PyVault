# Creates a "PyVault" shortcut on your Desktop, with the PyVault icon.
#
# How to use it:
#   1. Right-click this file (make_shortcut.ps1).
#   2. Choose "Run with PowerShell".
#   3. A PyVault shortcut appears on your Desktop - double-click it to start.
#
# You only need to do this once. Nothing is installed and nothing is changed
# outside of that one shortcut file.

# -Quiet is used when run.bat calls this during setup: no banner, no
# "press Enter", because run.bat is already talking to the user.
param([switch]$Quiet)

$ErrorActionPreference = 'Stop'

# Everything is found relative to this script, so PyVault can live in any folder.
$appDir   = $PSScriptRoot
$target   = Join-Path $appDir 'run.bat'
$icon     = Join-Path $appDir 'pyvault.ico'
$linkPath = Join-Path ([Environment]::GetFolderPath('Desktop')) 'PyVault.lnk'

if (-not (Test-Path $target)) {
    Write-Host "============================================================"
    Write-Host " Could not find run.bat next to this script."
    Write-Host " Keep make_shortcut.ps1 inside the PyVault folder and"
    Write-Host " right-click it again."
    Write-Host "============================================================"
    if (-not $Quiet) { Read-Host "Press Enter to close" }
    exit 1
}

$shell    = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($linkPath)
$shortcut.TargetPath       = $target
$shortcut.WorkingDirectory = $appDir
$shortcut.Description      = 'PyVault - password manager'

# 7 = minimized. run.bat exits the moment the app is handed off, so this
# stops the console flashing on screen during the hand-off.
$shortcut.WindowStyle = 7

# The icon is optional; a missing .ico shouldn't stop the shortcut being made.
if (Test-Path $icon) {
    $shortcut.IconLocation = "$icon,0"
} elseif (-not $Quiet) {
    Write-Host "Note: pyvault.ico is missing, so the shortcut will use the default icon."
}

$shortcut.Save()

# Windows caches shortcut icons, so nudge Explorer to redraw it.
try { & ie4uinit.exe -show } catch { }

if (-not $Quiet) {
    Write-Host ""
    Write-Host "Done - 'PyVault' is on your Desktop. Double-click it to start."
    Read-Host "Press Enter to close"
}
