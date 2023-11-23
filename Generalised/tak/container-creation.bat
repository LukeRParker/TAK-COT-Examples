ECHO OFF

IF EXIST ".\tak-server" rd /s /q ".\tak-server"

SET RESOURCE=takserver-docker-*.zip
SET CERT=.\shared\Takserver-Admin-1.p12

FOR /F "tokens=* delims=" %%i IN ('powershell -command "(dir %RESOURCE%).Basename"') DO set RESOURCE_FOLDER=%%i

python core_config_creator.py

ECHO "Unzipping TAK Server Docker Release"

powershell -command "Expand-Archive -Force '%~dp0%RESOURCE%' '%~dp0'"
powershell -command "do {try {Rename-Item -Path "%RESOURCE_FOLDER%" -NewName "tak-server" -ErrorAction Stop} catch {Start-Sleep -Seconds 5}} until (Test-Path "tak-server")"

ECHO "Inserting customised cert-metadata.sh and pg_hba.conf files"

copy /Y cert-metadata.sh .\tak-server\tak\certs\cert-metadata.sh
copy /Y pg_hba.conf .\tak-server\tak\db-utils\pg_hba.conf

ECHO "Building TAK Server and Database container images"
docker build -f Dockerfile-takserver -t stormcloud-takserver-k8s:latest .
docker build -f Dockerfile-takserver-db -t stormcloud-takserver-db-k8s:latest .
