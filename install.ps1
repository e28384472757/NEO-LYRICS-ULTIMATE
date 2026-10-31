$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$AppDir = Join-Path $env:LOCALAPPDATA 'Programs\NEO-LYRICS-ULTIMATE'
$Venv = Join-Path $AppDir '.venv'
if (-not (Get-Command py -ErrorAction SilentlyContinue)) { throw 'Python 3.10+ no encontrado. Instálalo desde python.org y vuelve a ejecutar.' }
New-Item -ItemType Directory -Force -Path $AppDir | Out-Null
Copy-Item -Path (Join-Path $Root '*') -Destination $AppDir -Recurse -Force
py -3 -m venv $Venv
& (Join-Path $Venv 'Scripts\python.exe') -m pip install --upgrade pip
& (Join-Path $Venv 'Scripts\python.exe') -m pip install "$AppDir[gui,windows]"
$Scripts = Join-Path $Venv 'Scripts'
$UserBin = Join-Path $env:LOCALAPPDATA 'NEO-LYRICS-ULTIMATE\bin'
New-Item -ItemType Directory -Force -Path $UserBin | Out-Null
$Launcher = Join-Path $UserBin 'neolyrics.cmd'
@"
@echo off
"$Scripts\neolyrics.exe" %*
"@ | Set-Content -Encoding ASCII $Launcher
$UserPath = [Environment]::GetEnvironmentVariable('Path','User')
if (($UserPath -split ';') -notcontains $UserBin) { [Environment]::SetEnvironmentVariable('Path', (($UserPath.TrimEnd(';') + ';' + $UserBin).Trim(';')), 'User') }
Write-Host "Instalado. Abre una nueva PowerShell y ejecuta neolyrics.cmd"
