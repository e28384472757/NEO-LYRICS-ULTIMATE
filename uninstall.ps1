$ErrorActionPreference = 'Stop'
Remove-Item -Recurse -Force (Join-Path $env:LOCALAPPDATA 'Programs\NEO-LYRICS-ULTIMATE') -ErrorAction SilentlyContinue
Remove-Item -Recurse -Force (Join-Path $env:LOCALAPPDATA 'NEO-LYRICS-ULTIMATE\bin') -ErrorAction SilentlyContinue
Write-Host 'NEO-LYRICS ULTIMATE desinstalado.'
