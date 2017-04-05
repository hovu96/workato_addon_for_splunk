@echo off
set DEPOY_PATH=%~dp0
set DEPOY_PATH=%DEPOY_PATH:\=/%
set DEPOY_PATH=%DEPOY_PATH:c:=/c%
IF %DEPOY_PATH:~-1%==/ SET DEPOY_PATH=%DEPOY_PATH:~0,-1%

@FOR /f "tokens=*" %%i IN ('docker-machine.exe env --shell cmd default') DO %%i

docker run --rm -it -v %DEPOY_PATH%/../:/workato_addon_for_splunk/:rw -w /workato_addon_for_splunk/deploy perl sh deploy.sh