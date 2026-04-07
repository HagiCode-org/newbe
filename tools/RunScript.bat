@echo off
%~d0
cd %~dp0
powershell -NoProfile -NonInteractive -ExecutionPolicy unrestricted -Command "& {invoke-psake %*; if ($global:lastexitcode -and $global:lastexitcode -ne 0) {write-host "ERROR CODE: $global:lastexitcode" -fore RED; exit $global:lastexitcode} }"