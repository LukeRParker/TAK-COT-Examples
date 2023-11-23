import base64

db_password = input("Please enter a password for the database: ")
ca_password = input("Please enter a password for the TAK Server Certificate Authority: ")

coreconfig = f"""<?xml version="1.0" encoding="UTF-8"?>
<Configuration xmlns="http://bbn.com/marti/xml/config"
               xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
               xsi:schemaLocation="CoreConfig.xsd">
    <network multicastTTL="5">
        <input _name="stdssl" protocol="tls" port="8089" auth="x509"/> 
        <connector port="8443" _name="https"/>
        <connector port="8444" useFederationTruststore="true" _name="fed_https"/>
        <connector port="8446" clientAuth="false" _name="cert_https"/>
    </network>
    <auth>
        <File location="UserAuthenticationFile.xml"/>
    </auth>
    <submission ignoreStaleMessages="false" validateXml="false"/>
    <subscription reloadPersistent="false">
    </subscription>
    <repository enable="true" numDbConnections="16" primaryKeyBatchSize="500" insertionBatchSize="500">
        <connection url="jdbc:postgresql://tak-database:5432/cot" username="martiuser" password="{db_password}" />
    </repository>
    <repeater enable="true" periodMillis="3000" staleDelayMillis="15000">
        <repeatableType initiate-test="/event/detail/emergency[@type='911 Alert']" cancel-test="/event/detail/emergency[@cancel='true']" _name="911"/>
        <repeatableType initiate-test="/event/detail/emergency[@type='Ring The Bell']" cancel-test="/event/detail/emergency[@cancel='true']" _name="RingTheBell"/>
        <repeatableType initiate-test="/event/detail/emergency[@type='Geo-fence Breached']" cancel-test="/event/detail/emergency[@cancel='true']" _name="GeoFenceBreach"/>
        <repeatableType initiate-test="/event/detail/emergency[@type='Troops In Contact']" cancel-test="/event/detail/emergency[@cancel='true']" _name="TroopsInContact"/>
    </repeater>
    <dissemination smartRetry="false" />
    <filter>
        <flowtag enable="false" text=""/>
        <streamingbroker enable="true"/>
        <scrubber enable="false" action="overwrite"/>
    </filter>
    <buffer>
        <latestSA enable="true"/>
        <queue/>
    </buffer>
    <security>
        <tls context="TLSv1.2"
             keymanager="SunX509"
             keystore="JKS" keystoreFile="/opt/tak/certs/files/takserver.jks" keystorePass="{ca_password}"
             truststore="JKS" truststoreFile="/opt/tak/certs/files/truststore-root.jks" truststorePass="{ca_password}">
        </tls>
    </security>
</Configuration>"""

with open("CoreConfig.xml",'w') as f:
    f.write(coreconfig)

ca_password = (base64.b64encode(ca_password.encode())).decode()

ca_secret = f"""apiVersion: v1
data:
  password: {ca_password}
kind: Secret
metadata:
  creationTimestamp: null
  labels:
    io.kompose.service: ca_password
  name: ca-password
  namespace: default
type: Opaque
"""

with open("./deployment/ca-password-secret.yaml",'w') as f:
    f.write(ca_secret)


db_password = (base64.b64encode(db_password.encode())).decode()

db_secret = f"""apiVersion: v1
data:
  dbpassword: {db_password}
kind: Secret
metadata:
  creationTimestamp: null
  labels:
    io.kompose.service: db_password
  name: db-password
  namespace: default
type: Opaque
"""

with open("./deployment/db-password-secret.yaml",'w') as f:
    f.write(db_secret)