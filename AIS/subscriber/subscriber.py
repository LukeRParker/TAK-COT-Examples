#Needs to be written up better to enable re-use. Generic version needed along with pub and sub component.

import asyncio
import pytak
from make_pem import convert_cert
from confluent_kafka import Consumer, KafkaException
from configparser import ConfigParser
import time
import os 

#Needs to be provided via the K8s yaml
#CAPASSWORD = "./AIS/subscriber/<your-ca-password-file>.txt"
#CERTPATH = "./AIS/subscriber/<your-TAK-server-certificate>.p12"

# Get the file paths
CERTPATH = str(os.path.join('/etc/ssl/certs', 'certificate.p12'))
CAPASSWORD = str(os.path.join('/etc/ssl/certs', 'password.key'))

# Read the contents of the key file
with open(CAPASSWORD, 'r') as file:
    #password = file.read().strip()
    password = file.read().rstrip('\n')
  
tak_server_host = str(os.getenv("TAKHOST"))
tak_server_port = str(os.getenv("TAKPORT"))
method = str(os.getenv("TAKCONMETHOD"))

bootstrap_server = str(os.getenv("KAFKANAME")) + ':' + str(os.getenv("KAFKAPORT"))
kafka_topic = str(os.getenv("KAFKATOPIC"))
kafka_consumer_group = str(os.getenv("KAFKACONSUMERGP"))
kafka_offset = str(os.getenv("KAFKAOFFSET"))

tak_server_connection = method + tak_server_host + ":" + tak_server_port
tak_server_cert_paths = convert_cert(CERTPATH,password)

# Create a Kafka consumer
c = Consumer({
    'bootstrap.servers': bootstrap_server,
    'group.id': kafka_consumer_group,
    'auto.offset.reset': kafka_offset
})

# Try to subscribe to the 'ais' topic
while True:
    try:
        c.subscribe([kafka_topic])
        print(f"Subscribed to topic {kafka_topic}")
        break
    except KafkaException as e:
        print(f"Failed to subscribe to topic {kafka_topic}: {e}, retrying in 1 second...")
        time.sleep(1)

class MySerializer(pytak.QueueWorker):
    """
    Defines how you process or generate Cursor-On-Target (CoT) Events.
    From there it adds the CoT Events to a queue for TX to a COT_URL.
    """
    async def handle_data(self, data):
        """
        Handles pre-CoT data and serializes to CoT Events, then puts on queue.
        """
        event = data
        await self.put_queue(event)
        
    async def run(self, number_of_iterations=-1):
        """
        Runs the loop for processing or generating pre-CoT data.
        """
        while 1:

            msg = c.poll(1.0) #timeout
            if msg is None:
                await asyncio.sleep(1)
                continue
            if msg.error():
                print('Error: {}'.format(msg.error()))
                await asyncio.sleep(10)
                continue

            if msg is not None:
                try:
                    # Parse the XML message
                    data = msg.value()
                    await self.handle_data(data)
                    continue
                except Exception as e:
                    print(f"Failed to parse XML message: {e}")
                    continue
            else:
                continue
        c.close()

async def main():
    """
    The main definition of the program, sets config params and
    adds the serializer to the asyncio task list.
    """
    config = ConfigParser()
    config["mycottool"] = {"COT_URL": tak_server_connection, "PYTAK_TLS_CLIENT_CERT": tak_server_cert_paths['cert_pem_path'], "PYTAK_TLS_CLIENT_KEY": tak_server_cert_paths['pk_pem_path'], "PYTAK_TLS_DONT_CHECK_HOSTNAME": "1", "PYTAK_TLS_DONT_VERIFY": "1"}    
    config = config["mycottool"]

    # Initializes worker queues and tasks.
    clitool = pytak.CLITool(config)
    await clitool.setup()

    # Add your serializer to the asyncio task list.
    clitool.add_tasks(set([MySerializer(clitool.tx_queue, config)]))
    # Start all tasks.
    await clitool.run()

if __name__ == "__main__":
    asyncio.run(main())