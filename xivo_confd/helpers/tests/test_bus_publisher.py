# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

from mock import Mock, sentinel
import unittest
from xivo_confd.helpers.bus_publisher import BusPublisher


CONFIG = {
    'bus': {
        'host': 'example.org',
        'port': 5672,
        'username': 'foo',
        'password': 'bar',
        'exchange_name': 'xivo',
        'exchange_type': 'topic',
    },
    'uuid': '111-2222',
}


class TestBusContext(unittest.TestCase):

    def test_new_from_config(self):
        publisher = BusPublisher.from_config(CONFIG)

        self.assertEqual(publisher.url, 'amqp://foo:bar@example.org:5672//')
        self.assertEqual(publisher.exchange_name, 'xivo')
        self.assertEqual(publisher.exchange_type, 'topic')
        self.assertEqual(publisher.uuid, '111-2222')

    def test_send_messages(self):
        publish_func = Mock()
        publisher = BusPublisher.from_config(CONFIG)
        marshaler = Mock()
        marshaler.marshal_message.return_value = sentinel.event

        publisher.send_bus_event(sentinel.unmarshaled_event, sentinel.routing_key)
        publisher.send_messages(marshaler, publish_func)

        publish_func.assert_called_once_with(sentinel.event, routing_key=sentinel.routing_key)
