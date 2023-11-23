#!/bin/sh

if [ $# -eq 0 ]
  then
    ps -ef | grep takserver | grep -v grep | awk '{print $2}' | xargs kill
fi

cd /opt/tak || echo "Something is wrong in container"
. ./setenv.sh
java -jar -Xmx"${MESSAGING_MAX_HEAP}"m -Dspring.profiles.active=messaging takserver.war &
java -jar -Xmx"${API_MAX_HEAP}"m -Dspring.profiles.active=api -Dkeystore.pkcs12.legacy takserver.war &
java -jar -Xmx"${PLUGIN_MANAGER_MAX_HEAP}"m takserver-pm.jar &

#if [ ! -d /opt/tak/certs/files ];
  #then
    #echo "Running the Army Software Factory Configurator"
    #/opt/configurator/configurator.sh
#fi

#Changed to allow persistence of certs in the case of a pod restart
if [ ! -d /opt/tak/certs/files ] || [ -z "$(ls -A /opt/tak/certs/files)" ];
  then
    echo "Running the Army Software Factory Configurator"
    /opt/configurator/configurator.sh
fi


if ! [ $# -eq 0 ]
  then
    tail -f /dev/null
fi
 