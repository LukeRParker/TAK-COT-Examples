import time
import os
from pyais.stream import TCPConnection
from confluent_kafka import Producer
from make_cot import mkcot
import redis

ais_host = str(os.getenv("AISHOST"))
ais_port = int(os.getenv("AISPORT"))

message_stale_time = int(os.getenv("MSGSTALE"))
data_source = str(os.getenv("DATASOURCE"))

redis_host = str(os.getenv("REDISHOST"))
redis_port = int(os.getenv("REDISPORT"))

rn = redis.Redis(host=redis_host, port=redis_port, db=0)

non_dup_messages = []

bootstrap_server = str(os.getenv("KAFKANAME")) + ':' + str(os.getenv("KAFKAPORT"))
kafka_topic = str(os.getenv("KAFKATOPIC"))

def delivery_report(err, msg):
    """
    Checks produced message has been delivered to Kafka.

    Parameters:
    err (if present), msg.

    Returns:
    Error message (if error occurs). 
    Otherwise returns the topic and partition the message was published to.
    """
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")

p = Producer({'bootstrap.servers': bootstrap_server})

def handle_connection(host, port):
    """
    Performs the following functions:
    1. Handles the TCP connection to the AIS feed.
    2. Decodes the AIS message.
    3. Detects the AIS message type.
    4. Converts the AIS message to COT XML (if message is of type 1, 3, or 18).
    5. Inserts the ship's name as the COT callsign once known from AIS message types 5/24 Part A.
    6. Publishes COT XML message to Kafka.

    Parameters:
    Host: IP address of the AIS feed.
    Port: Port for the AIS feed at the given IP.

    Returns:
    Error message (if error occurs). Otherwise prints logs to console.
    """
    for msg in TCPConnection(host, port=port):
        decoded_message = msg.decode()
        ais_content = decoded_message

        if ais_content.msg_type in (1,3,18):

            shipname = rn.hget(ais_content.mmsi,'shipname')
            if shipname is None:
                shipname = ais_content.mmsi
            else:
                shipname = shipname.decode('utf-8')

            shiptype = rn.hget(ais_content.mmsi,'shiptype')
            if shiptype is None:
                shiptype = '90'
            else:
                shiptype = shiptype.decode('utf-8')

            speed_ms = float(ais_content.speed) * 0.1 / 1.944 #Convert kts to m/s.
            
            data = mkcot(
                ais_content.mmsi,
                ais_content.lat,
                ais_content.lon,
                speed_ms,
                ais_content.heading,
                "unknown",
                str(shiptype),
                None,
                str(shipname),
                None,
                None,
                None,
                None,
                message_stale_time, 
                data_source
            )
            
            #print(data) #Uncomment to see the XML messages for testing.
            p.produce(kafka_topic, data.encode('utf-8'), callback=delivery_report)
            p.flush()

        if ais_content.msg_type in (5,24):

            try:
                mmsi = ais_content.mmsi
                if rn.hexists(mmsi,'shipname'):
                    print('Ship name already identified.')
                else:
                    rn.hset(mmsi,'shipname',ais_content.shipname)
                
                if ais_content.msg_type == 5:
                    try:
                        if rn.hexists(mmsi,'shiptype'):
                            print('Ship type already known.')
                        else:
                            match = ais_content.ship_type.value
                            if match:
                                rn.hset(mmsi,'shiptype',match)
                            else:
                                rn.hset(mmsi,'shiptype','90')
                    except Exception as e:
                        print(f'Error: {e}')
            except Exception:
                print('Ignore: Message Type 24 Part B - No Ship Name')

# Try to establish the TCP connection and handle it
while True:
    try:
        rn.ping()
        handle_connection(ais_host,ais_port)
    except Exception as e:
        print(f"Error occurred: {e}")
        print("Reconnecting in 60 seconds...")
        time.sleep(60) # Wait for 1 minute before trying to reconnect