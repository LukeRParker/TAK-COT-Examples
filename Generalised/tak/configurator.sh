#!/bin/bash

cd /opt/tak/certs || echo "Something is wrong in Takserver Container"

JPSOUT=$(jps | grep takserver-pm | cut -d " " -f 1)

echo "Creating Root Certificate / Server Certificate / Admin Certificate / User Certificate"

./makeRootCa.sh --ca-name root-ca && ./makeCert.sh server takserver

for i in $(seq 1 "$ADMINS_COUNT")
do
  ./makeCert.sh client "Takserver-Admin-$i"
done

for i in $(seq 1 "$USER_COUNT")
do
  ./makeCert.sh client "Takserver-User-$i"
done

chmod +x /opt/tak/utils/UserManager.jar

until jmap -histo:live "$JPSOUT" | grep "tak.server.plugins.messaging.PluginMessenger"
do
    sleep 1
done

for i in $(seq 1 "$ADMINS_COUNT")
do
    java -jar /opt/tak/utils/UserManager.jar certmod -A /opt/tak/certs/files/Takserver-Admin-"$i".pem | tee -a scrape_file.txt
done

for i in $(seq 1 "$USER_COUNT")
do
    java -jar /opt/tak/utils/UserManager.jar usermod -c /opt/tak/certs/files/Takserver-User-"$i".pem Takserver-User-"$i" | tee -a scrape_file.txt
done


