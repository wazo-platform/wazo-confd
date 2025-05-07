# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from wazo_bus.resources.endpoint_iax.event import (
    IAXEndpointCreatedEvent,
    IAXEndpointDeletedEvent,
    IAXEndpointEditedEvent,
)
from xivo_dao.alchemy.useriax import UserIAX as IAX

from ..notifier import IAXEndpointNotifier

SYSCONFD_HANDLERS = {'ipbx': ['iax2 reload']}


class TestIAXEndpointNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.iax = Mock(IAX, id=1, tenant_uuid=str(uuid.uuid4), trunk_rel={'id': 2})
        self.iax.name = 'limitation of mock instantiation with name ...'
        self.iax_serialized = {
            'id': self.iax.id,
            'tenant_uuid': self.iax.tenant_uuid,
            'name': self.iax.name,
            'trunk': self.iax.trunk_rel,
        }

        self.notifier = IAXEndpointNotifier(self.sysconfd, self.bus)

    def test_when_iax_endpoint_created_then_event_sent_on_bus(self):
        expected_event = IAXEndpointCreatedEvent(
            self.iax_serialized, self.iax.tenant_uuid
        )

        self.notifier.created(self.iax)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_iax_endpoint_edited_then_iax_reloaded(self):
        self.notifier.edited(self.iax)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_iax_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = IAXEndpointEditedEvent(
            self.iax_serialized, self.iax.tenant_uuid
        )

        self.notifier.edited(self.iax)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_iax_endpoint_deleted_then_iax_reloaded(self):
        self.notifier.deleted(self.iax)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_iax_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = IAXEndpointDeletedEvent(
            self.iax_serialized, self.iax.tenant_uuid
        )

        self.notifier.deleted(self.iax)

        self.bus.queue_event.assert_called_once_with(expected_event)
