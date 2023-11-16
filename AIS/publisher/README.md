# AIS Live Data Publisher

The Norwegian Coastal Administration offers real-time AIS data.
This live feed can be accessed via TCP/IP without prior registration.
The AIS data is freely available under the norwegian license for public data:

- https://data.norge.no/nlod/no/1.0
- https://kystverket.no/navigasjonstjenester/ais/tilgang-pa-ais-data/

Data can be read from a TCP/IP socket and is encoded according to IEC 62320-1:

- IP:   153.44.253.27
- Port: 5631

This section of the repo implements the following:

1. Listens to the real-time AIS data from the above TCP/IP socket (provided via publisher.yaml). This could be modified for any TCP/IP socket that provides AIS, or altered to support other collection methods. The [GitHub repo for PyAIS](https://github.com/M0r13n/pyais) provides a number of examples.

2. If the AIS message is of Type 1, 3, or 18, key track data is extracted from the message, namely MMSI (unique id), lat, lon, speed, course. Other data elements are available and could be extracted for other purposes.

3. If the AIS message is of Type 5 or 24 (Type A), the ship's name is extracted from the message and added to a Redis store which maps MMSI to ship name. 

4. The data extracted from AIS Type 1, 3 or 18 messages is converted to Cursor on Target (CoT) XML format (this could be modified to support any other data format).

5. Where the ship name is known (ie referenced within the Redis store), this is used as the callsign. Where the ship name is not known, the MMSI is used as the callsign.

6. If the AIS message is of Type 5, the ship's type is extracted from the message and added to the same Redis store as part of a hash containing MMSI mapped to ship name and ship type fields.

7. The CoT XML message created from the AIS data is then published to Kafka.

CoT types for AIS are based on https://github.com/dB-SPL/cot-types/blob/main/CoTtypes.xml and detailed in *ais_cot_types.xml* referenced from *make_cot.py*.

## Quickstart

1. Build the publisher component by running the following within the ./publisher folder.

```
docker build -f Dockerfile -t ais-publisher .
```

2. Deploy the publisher component and the Redis store to Kubernetes using publisher.yaml. Run the following within the ./publisher folder.

```
kubectl apply -f publisher.yaml
```