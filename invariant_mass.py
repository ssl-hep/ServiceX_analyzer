#!/usr/bin/env python
import awkward
import pyarrow as pa
import argparse
from kafka import KafkaConsumer
import uproot_methods

kakfa_brokers = []

parser = argparse.ArgumentParser(
    description='Compute invariant mass of electrons from Kafka.')

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
                             api_version=(0, 10), consumer_timeout_ms=1000,
                             group_id=None)

    running = True
    while running:
        raw_messages = consumer.poll(timeout_ms=1000, max_records=5000)
        if raw_messages != {}:
            for topic_partition, messages in raw_messages.items():
                for msg in messages:
                    buf = msg.value
                    reader = pa.ipc.open_stream(buf)
                    batches = [b for b in reader]
                    for batch in batches:
                        arrays = awkward.fromarrow(batch)
                        v_particles = uproot_methods.TLorentzVectorArray.from_ptetaphi(
                            arrays['Electrons_pt'], arrays['Electrons_eta'],
                            arrays['Electrons_phi'], arrays['Electrons_e'],
                        )
                        v_particles = v_particles[v_particles.counts >= 2]
                        print(v_particles.pt.tolist())
        else:
            running = False

except Exception as ex:
    print(ex)
    raise
