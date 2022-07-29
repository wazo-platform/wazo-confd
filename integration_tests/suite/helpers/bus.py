# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from kombu import Exchange, Connection
from wazo_test_helpers import bus


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

        event = {
            'name': 'auth_tenant_added',
            'data': {'uuid': tenant_uuid, 'slug': slug},
        }
        self.publish(event, headers={'name': event['name']})

    def send_tenant_deleted(self, tenant_uuid, slug='slug'):
        if self.exchange_type != 'headers':
            raise NotImplementedError()

        event = {
            'name': 'auth_tenant_deleted',
            'data': {'uuid': tenant_uuid, 'slug': slug},
        }
        self.publish(event, headers={'name': event['name']})

    def send_meeting_reload_complete_event(self, meeting):
        event = {
            'name': 'request_handlers_progress',
            'data': {
                'uuid': '371b64b9-1f45-4c56-9a8e-0672fde9d452',
                'status': 'completed',
                'context': [
                    {
                        'resource_type': 'meeting',
                        'resource_action': 'created',
                        'resource_body': {'uuid': meeting['uuid']},
                    }
                ],
            },
        }
        self.publish(event, headers={'name': event['name']})


BusClient = BusClientWrapper()


def setup_bus(host, port):
    # Register `xivo(topic)` -> `wazo-headers(headers)``
    with Connection(hostname=host, port=port) as connection:
        topic = Exchange('xivo', 'topic', channel=connection)
        topic.declare()
        headers = Exchange('wazo-headers', 'headers', channel=connection)
        headers.declare()
        headers.bind_to(topic, routing_key='#')

    BusClient.host = host
    BusClient.port = port
    BusClient.exchange_name = 'wazo-headers'
    BusClient.exchange_type = 'headers'
