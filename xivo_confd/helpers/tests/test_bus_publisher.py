# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

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
        metadata_headers = {'name': 'event-name'}
        custom_headers = {'custom': 'value'}
        expected_headers = {'name': 'event-name', 'custom': 'value'}
        publish_func = Mock()
        publisher = BusPublisher.from_config(CONFIG)
        marshaler = Mock(content_type=sentinel.content_type)
        marshaler.marshal_message.return_value = sentinel.event
        marshaler.metadata.return_value = metadata_headers

        publisher.send_bus_event(sentinel.unmarshaled_event, sentinel.routing_key, headers=custom_headers)
        publisher.send_messages(marshaler, publish_func)

        publish_func.assert_called_once_with(sentinel.event,
                                             routing_key=sentinel.routing_key,
                                             content_type=sentinel.content_type,
                                             headers=expected_headers)
