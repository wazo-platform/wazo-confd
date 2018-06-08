# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from kombu import Connection, Exchange, Producer
from xivo_bus import Marshaler, Publisher

logger = logging.getLogger(__name__)


class BusPublisher(object):

    @classmethod
    def from_config(cls, config):
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        bus_connection = Connection(bus_url)
        bus_exchange = Exchange(config['bus']['exchange_name'], type=config['bus']['exchange_type'])
        bus_producer = Producer(bus_connection, exchange=bus_exchange, auto_declare=True)
        bus_marshaler = Marshaler(config['uuid'])
        bus_publisher = Publisher(bus_producer, bus_marshaler)
        return cls(bus_publisher)

    def __init__(self, publisher):
        self._publisher = publisher
        self.messages = []

    def send_bus_event(self, event, headers=None):
        self.messages.append((event, headers))

    def flush(self):
        for event, headers in self.messages:
            self._publisher.publish(event, headers)

    def rollback(self):
        self.messages = []
