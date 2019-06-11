#!/usr/bin/env python
import awkward
import pyarrow as pa
import argparse

import sys
from confluent_kafka import Consumer, KafkaException
import uproot_methods
import logging

from coffea import hist
import matplotlib.pyplot as plt



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

# Create logger for consumer (logs will be emitted when poll() is called)
logger = logging.getLogger('consumer')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
logger.addHandler(handler)

try:
    conf = {'bootstrap.servers': args.broker, 'group.id': 'inv',
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest'}
    c = Consumer(conf, logger=logger)


    def print_assignment(consumer, partitions):
        print('Assignment:', partitions)


    # Subscribe to topics
    c.subscribe([args.topic], on_assign=print_assignment)

    timeout = 55.0 # Need a long timeout to allow for partition assignment
    running = True
    while running:
        msg = c.poll(timeout=timeout)
        if msg is None:
            running = False
            continue
        if msg.error():
            raise KafkaException(msg.error())
        else:
            # Proper message
            sys.stderr.write('%% %s [%d] at offset %d with key %s:\n' %
                             (msg.topic(), msg.partition(), msg.offset(),
                              str(msg.key())))

            buf = msg.value()
            reader = pa.ipc.open_stream(buf)
            batches = [b for b in reader]
            for batch in batches:
                arrays = awkward.fromarrow(batch)
                v_particles = uproot_methods.TLorentzVectorArray.from_ptetaphi(
                    arrays['Electrons_pt'], arrays['Electrons_eta'],
                    arrays['Electrons_phi'], arrays['Electrons_e'],
                )
                v_particles = v_particles[v_particles.counts >= 2]
                diparticles = v_particles[:, 0] + v_particles[:, 1]
                print("Diparticle mass: " + str(diparticles.mass))

                mass_hist = hist.Hist('Counts', hist.Bin('mass', r'$m_{\mu\mu}$ (GeV)', 150, 0.0, 150.0))
                mass_hist.fill(mass=diparticles.mass/1000.0)
                fig, ax, _ = hist.plot1d(mass_hist)
                plt.show()
                # Can add histograms via mass_hist.add(mass_hist_2)

                # Once we are assigned a partition and start getting messages
                # we can tighten up the timeout
                timeout = 10.0
except Exception as ex:
    print(ex)
    raise
