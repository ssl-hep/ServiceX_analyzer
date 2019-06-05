#!/usr/bin/env python
import awkward
import pyarrow as pa
import argparse
from kafka import KafkaConsumer

kakfa_brokers = []



parser = argparse.ArgumentParser(description='Compute invariant mass of electrons from Kafka.')

parser.add_argument("--broker", dest='broker', action='store',
                    default='localhost:9092',
                    help='Kafka broker to connect to')


parser.add_argument("--topic", dest='topic', action='store',
                    default='servicex',
                    help='Kafka topic to publish to')

args = parser.parse_args()

try:
    consumer = KafkaConsumer(args.topic, auto_offset_reset='earliest',
                             bootstrap_servers=[args.broker],
                             api_version=(0, 10), consumer_timeout_ms=1000)


    for msg in consumer:
        buf = msg.value
        reader = pa.ipc.open_stream(buf)
        batches = [b for b in reader]
        arrays = awkward.fromarrow(batches[0])
        print(arrays)
except Exception as ex:
    print(ex)
