# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import logging

logger = logging.getLogger(__name__)
_bus_publish = None
_marshaler = None


class BusContext(object):

    def __init__(self, url, exchange_name, exchange_type, uuid):
        self._url = url
        self._exchange_name = exchange_name
        self._exchange_type = exchange_type
        self._uuid = uuid

    def new_connection(self):
        from kombu import Connection
        return Connection(self._url)

    def new_bus_producer(self, connection):
        from kombu import Exchange, Producer
        exchange = Exchange(self._exchange_name, self._exchange_type)
        return Producer(connection, exchange=exchange, auto_declare=True)

    def new_marshaler(self):
        from xivo_bus import Marshaler
        return Marshaler(self._uuid)

    @classmethod
    def new_from_config(cls, config):
        url = 'amqp://{username}:{password}@{host}:{port}//'.format(**config['bus'])
        exchange_name = config['bus']['exchange_name']
        exchange_type = config['bus']['exchange_type']
        uuid = config['uuid']
        return cls(url, exchange_name, exchange_type, uuid)


def on_bus_context_update(bus_context):
    global _bus_publish
    global _marshaler

    def _on_bus_publish_error(exc, interval):
        logger.error('Error: %s', exc, exc_info=1)
        logger.info('Retry in %s seconds...', interval)

    bus_connection = bus_context.new_connection()
    bus_producer = bus_context.new_bus_producer(bus_connection)
    _bus_publish = bus_connection.ensure(bus_producer, bus_producer.publish,
                                         errback=_on_bus_publish_error, max_retries=3,
                                         interval_start=1)
    _marshaler = bus_context.new_marshaler()


def send_bus_event(event, routing_key):
    if not _bus_publish or not _marshaler:
        logger.warning('Trying to send %s on %s with an unconfigured bus', event, routing_key)
        return

    msg = _marshaler.marshal_message(event)
    _bus_publish(msg, routing_key=routing_key)


def init_bus(bus_context):
    on_bus_context_update(bus_context)


def init_bus_from_config(config):
    init_bus(BusContext.new_from_config(config))
