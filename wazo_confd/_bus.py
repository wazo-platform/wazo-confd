# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import kombu
import logging

from contextlib import contextmanager
from threading import Thread

from kombu.mixins import ConsumerMixin
from xivo_bus import Marshaler, Publisher
from xivo.pubsub import Pubsub

logger = logging.getLogger(__name__)


class BusPublisher:
    @classmethod
    def from_config(cls, bus_config, wazo_uuid):
        bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(**bus_config)
        bus_connection = kombu.Connection(bus_url)
        bus_exchange = kombu.Exchange(
            bus_config['exchange_name'], type=bus_config['exchange_type']
        )
        bus_producer = kombu.Producer(
            bus_connection, exchange=bus_exchange, auto_declare=True
        )
        bus_marshaler = Marshaler(wazo_uuid)
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


@contextmanager
def bus_consumer_thread(bus_consumer):
    thread_name = 'bus_consumer_thread'
    thread = Thread(target=bus_consumer.run, name=thread_name)
    thread.start()
    try:
        yield
    finally:
        logger.debug('stopping bus consumer thread')
        bus_consumer.should_stop = True
        thread.join()


class BusConsumer(ConsumerMixin):
    def __init__(self, bus_config):
        self._bus_url = 'amqp://{username}:{password}@{host}:{port}//'.format(
            **bus_config
        )
        self._exchange = kombu.Exchange(
            bus_config['subscribe_exchange_name'], type='headers'
        )
        self._queue = kombu.Queue(exclusive=True)
        self._pubsub = Pubsub()

    def run(self):
        logger.info("Running AMQP consumer")
        with kombu.Connection(self._bus_url) as connection:
            self.connection = connection  # For internal usage
            super().run()

    def get_consumers(self, Consumer, channel):
        return [Consumer(self._queue, callbacks=[self._on_bus_message])]

    def on_event(self, event_name, callback):
        logger.debug('Added callback on event "%s"', event_name)
        arguments = {'x-match': 'all', 'name': event_name}
        self._queue.bindings.add(kombu.binding(self._exchange, arguments=arguments))
        self._pubsub.subscribe(event_name, callback)

    def _on_bus_message(self, body, message):
        try:
            event_type = body['name']
            event = body['data']
        except KeyError:
            logger.error('Invalid event message received: %s', event)
            message.reject()
            return

        try:
            self._pubsub.publish(event_type, event)
        except Exception:
            message.reject()
            return

        message.ack()
