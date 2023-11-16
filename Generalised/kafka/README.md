# Example Kafka Deployment

The publisher/subscribers within this repo all use the same common Kafka example. If you don't already have Kafka running in K8s, you can use this example to get started.

This example uses the [Strimzi](https://strimzi.io/) Operator to make configuration and management of Kafka within K8s easier. However, you don't have to use Strimzi with the pub/sub examples.

To use Kafka in KRaft mode deployed via the Strimzi Operator, execute the following commands, ensuring that the previous command has completed successfully before executing the next.

The Strimzi Operator deployment has been captured in a yaml file for ease of reference.

```
kubectl create namespace kafka
kubectl apply -f strimzi-operator.yaml
kubectl apply -f strimzi-kafka-kraft.yaml
```