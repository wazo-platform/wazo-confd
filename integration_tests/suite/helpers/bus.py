# Copyright 2017-2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_test_helpers import bus


class BusClientWrapper:
    def __init__(self):
        self.host = None
        self.port = None
        self.exchange_name = None
        self.exchange_type = None
        self._bus = None

    def __getattr__(self, attr):
        if self._bus is None:
            self._bus = self._create_client()
        return getattr(self._bus, attr)

    def _create_client(self):
        return bus.BusClient.from_connection_fields(
            host=self.host,
            port=self.port,
            exchange_name=self.exchange_name,
            exchange_type=self.exchange_type,
        )

    def send_tenant_created(self, tenant_uuid, slug='slug'):
        if self.exchange_type != 'headers':
            raise NotImplementedError()

        if self._bus is None:
            self._bus = self._create_client()
        event = {
            'name': 'auth_tenant_added',
            'data': {'uuid': tenant_uuid, 'slug': slug},
        }
        self._bus.publish(event, headers={'name': event['name']})


BusClient = BusClientWrapper()
BusClientHeaders = BusClientWrapper()


def setup_bus(host, port):
    BusClient.host = host
    BusClient.port = port
    BusClient.exchange_name = 'xivo'
    BusClient.exchange_type = 'topic'

    BusClientHeaders.host = host
    BusClientHeaders.port = port
    BusClientHeaders.exchange_name = 'wazo-headers'
    BusClientHeaders.exchange_type = 'headers'
