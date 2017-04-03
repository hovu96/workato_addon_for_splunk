@echo off
set DEPOY_PATH=%~dp0
set DEPOY_PATH=%DEPOY_PATH:\=/%
set DEPOY_PATH=%DEPOY_PATH:c:=/c%
IF %DEPOY_PATH:~-1%==/ SET DEPOY_PATH=%DEPOY_PATH:~0,-1%

@FOR /f "tokens=*" %%i IN ('docker-machine.exe env --shell cmd default') DO %%i


docker rm -fv workato_splunk
docker rm -fv workato_test

set NETWORK_NAME="workato-integration-test"
docker network create %NETWORK_NAME%

docker run -p 8000:8000 --name workato_splunk -d -e "SPLUNK_START_ARGS=--accept-license" -e "SPLUNK_CMD=edit user admin -password admin -auth admin:changeme" -v %DEPOY_PATH%/../:/opt/splunk/etc/apps/workato_addon_for_splunk:rw -v %DEPOY_PATH%/test_app:/opt/splunk/etc/apps/test_app:rw --network %NETWORK_NAME% splunk/splunk:latest

docker run --name workato_test -it --rm -v %DEPOY_PATH%/test:/usr/src/myapp:ro -w /usr/src/myapp --network %NETWORK_NAME% python:2.7 python2.7 integration_test.py workato_splunk 8089 workato_test

set /p DUMMY=Hit ENTER to continue...
docker rm -fv workato_splunk

rem @for /f %%i in ('docker-machine.exe inspect --format="{{.HostOptions.AuthOptions.StorePath}}" default') do set DOCKER_MACHINE_STORE_PATH=%%i
rem set DOCKER_MACHINE_STORE_PATH=%DOCKER_MACHINE_STORE_PATH:\=/%
rem set DOCKER_MACHINE_STORE_PATH=%DOCKER_MACHINE_STORE_PATH:c:=/c%

rem docker rm -fv workato_test_env
rem docker build -t workato_test_env -f=test_Dockerfile ..

rem docker run --rm -v="%DOCKER_MACHINE_STORE_PATH%:/dockermachine:ro" --env DOCKER_HOST="%DOCKER_HOST%" --env DOCKER_TLS_VERIFY="%DOCKER_TLS_VERIFY%" --env DOCKER_CERT_PATH="/dockermachine" --env ADDON_PATH="%PWD%" -it --name workato_test_env workato_test_env 