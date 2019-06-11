# Copyright (c) 2019, IRIS-HEP
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the copyright holder nor the names of its
#   contributors may be used to endorse or promote products derived from
#   this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
import pickle

import awkward
import lz4.frame as lz4f
import pyarrow as pa
import argparse

import sys
from confluent_kafka import Consumer, KafkaException, Producer
import uproot_methods
import logging

from coffea import hist
import matplotlib.pyplot as plt
import coffea.hist.plot as coffeaplot

kakfa_brokers = []

parser = argparse.ArgumentParser(
    description='Compute invariant mass of electrons from Kafka.')

parser.add_argument("--broker", dest='broker', action='store',
                    default='localhost:9092',
                    help='Kafka broker to connect to')

parser.add_argument("--hist-topic", dest='hist_topic', action='store',
                    default='hists',
                    help='Kafka topic to publish histograms to')

args = parser.parse_args()



# Create logger for consumer (logs will be emitted when poll() is called)
logger = logging.getLogger('consumer')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter('%(asctime)-15s %(levelname)-8s %(message)s'))
logger.addHandler(handler)

accumulate = None

try:
    conf = {'bootstrap.servers': args.broker, 'group.id': 'hist',
            'session.timeout.ms': 6000,
            'auto.offset.reset': 'earliest'}
    c = Consumer(conf, logger=logger)


    def print_assignment(consumer, partitions):
        print('Assignment:', partitions)

    # Subscribe to topics
    c.subscribe([args.hist_topic], on_assign=print_assignment)

    timeout = 55.0  # Need a long timeout to allow for partition assignment
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
            hist = pickle.loads(lz4f.decompress(buf))
            if accumulate:
                accumulate = accumulate.add(hist)
            else:
                accumulate = hist

            # Once we are assigned a partition and start getting messages
            # we can tighten up the timeout
            timeout = 10.0

    print(accumulate.values())
    fig, ax, _ = coffeaplot.plot1d(accumulate)
    plt.savefig("/servicex/plot.png")


except Exception as ex:
    print(ex)
    raise
