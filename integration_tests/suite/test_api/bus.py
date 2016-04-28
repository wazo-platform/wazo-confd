# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from kombu import Connection
from kombu import Consumer
from kombu import Exchange
from kombu import Queue
from kombu.exceptions import TimeoutError

BUS_EXCHANGE_NAME = 'xivo'
BUS_EXCHANGE_TYPE = 'topic'
BUS_URL = 'amqp://guest:guest@localhost:5672//'
BUS_QUEUE_NAME = 'integration'


class BusClient(object):

    @classmethod
    def listen_events(cls, routing_key, exchange=BUS_EXCHANGE_NAME):
        exchange = Exchange(exchange, type=BUS_EXCHANGE_TYPE)
        with Connection(BUS_URL) as conn:
            queue = Queue(BUS_QUEUE_NAME, exchange=exchange, routing_key=routing_key, channel=conn.channel())
            queue.declare()
            queue.purge()
            cls.bus_queue = queue

    @classmethod
    def events(cls):
        events = []

        def on_event(body, message):
            events.append(body)
            message.ack()

        cls._drain_events(on_event=on_event)

        return events

    @classmethod
    def _drain_events(cls, on_event):
        with Connection(BUS_URL) as conn:
            with Consumer(conn, cls.bus_queue, callbacks=[on_event]):
                try:
                    while True:
                        conn.drain_events(timeout=0.5)
                except TimeoutError:
                    pass
