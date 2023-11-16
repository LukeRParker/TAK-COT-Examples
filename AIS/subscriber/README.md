# AIS Live Data Subscriber

This section of the repo implements the following:

1. Creates a subscriber service that listens to the topic that the publisher has produced AIS messages in CoT format on.

2. Uses the Kubernetes secret containing the .p12 TLS certificate and password to convert to .pem and store in a temporary file on the pod. This .pem file is used to create the subscriber service's TLS connection to TAK Server.

3. AIS messages in CoT format are picked up from Kafka, and sent to TAK Server.

## Quickstart

1. Build the subscriber component by running the following within the *./subscriber* folder.

```
docker build -f Dockerfile -t tak-ais-subscriber .
```

2. Run the following command, ensuring that you reflect the path to a valid .p12 TLS certificate for a TAK client, and path to the .key file that contains the password for the .p12 certificate.

```
kubectl create secret generic tak-client-tls-cert --from-file=certificate.p12=<PATH/TO/TAK/P12/FILE> --from-file=password.key=<PATH/TO/TAK/KEY/FILE>
```

3. Deploy the subcriber component to Kubernetes using *subscriber.yaml*. Run the following within the *./subscriber* folder.

```
kubectl apply -f subscriber.yaml
```
