# Kubernetes and Kafka TAK CoT Scenarios

This repo contains examples written in Python for adapter patterns that enable:

1. Data to be converted into a Cursor on Target (CoT) XML format that is suitable for ingestion into TAK Server.

2. Publishing of these XML messages to Kafka.

3. Consumption of these XML messages from Kafka by a TAK Client that forwards the message to TAK Server for other Clients to consume.

Ultimately it is a design choice as to whether data is converted to CoT XML before being published to Kafka, or published to Kafka in a format such as JSON, and then converted by the subscriber to CoT XML. The examples within this repo could be refactored to support the conversion to CoT XML occurring on the subscriber vice publisher component.

## ./Generalised

Here you'll find:

- **./publisher**: A generalised example of a Python script for generating CoT XML messages with an associated XML schema reference point for CoT types within the XML standard.

- **./kafka**: Yaml files for deploying a simple Kafka cluster in KRaft mode using the Strimzi Operator.

- **./tak**: A simplified set of files and scripts for building container images of TAK Server and it's PostgreSQL database, and then deploying them to Kubernetes.

## Work in Progress

- Generalised example of a publisher and subscriber.
- Further examples beyond AIS.

## Other Works

These examples build on some of the foundational work and use cases developed by Sensors & Signals LLC - https://github.com/snstac under Apache License 2.0.