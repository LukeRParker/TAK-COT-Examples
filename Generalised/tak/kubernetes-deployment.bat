ECHO OFF

ECHO "Deploying TAK Server to Kubernetes"
kubectl apply -f deployment/
timeout /t 30

ECHO "TAK Server Deployed to Kubernetes"

FOR /F "delims=" %%i IN ('"kubectl get pods --no-headers -o custom-columns=":metadata.name" | findstr /R ".*takserver.*""') DO SET POD_NAME=%%i

kubectl cp --retries=-1 %POD_NAME%:opt/tak/certs/files/Takserver-Admin-1.p12 ./shared/Takserver-Admin-1.p12
kubectl cp --retries=-1 %POD_NAME%:opt/tak/certs/files/Takserver-User-1.p12 ./shared/Takserver-User-1.p12
kubectl cp --retries=-1 %POD_NAME%:opt/tak/certs/files/truststore-root.p12 ./shared/truststore-root.p12

kubectl cp --retries=-1 %POD_NAME%:opt/tak/certs/files/Takserver-Admin-1.pem ./shared/Takserver-Admin-1.pem
kubectl cp --retries=-1 %POD_NAME%:opt/tak/certs/files/Takserver-Admin-1.key ./shared/Takserver-Admin-1.key

ECHO "Waiting for TAK Server TLS Certificate Generation (this can take up to a few minutes)"

SET FOUND=false
:loop
IF EXIST %CERT% SET FOUND=true
IF %FOUND%==true GOTO :exitloop
GOTO :loop
:exitloop

ECHO "TAK Server Admin Certificate Found. Creating Kubernetes Secret for the Admin Certificate."

kubectl create secret generic takserver-cert-pem --from-file=./shared/Takserver-Admin-1.pem --namespace=default
kubectl create secret generic takserver-cert-key --from-file=./shared/Takserver-Admin-1.key --namespace=default
