# Copyright 2018-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.call_pickup.event import (
    CallPickupCreatedEvent,
    CallPickupDeletedEvent,
    CallPickupEditedEvent,
)
from xivo_dao.alchemy.pickup import Pickup as CallPickup

from ..notifier import CallPickupNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so']
}


class TestCallPickupNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.call_pickup = Mock(CallPickup, id=1234, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.call_pickup.tenant_uuid}

        self.notifier = CallPickupNotifier(self.bus, self.sysconfd)

    def test_when_call_pickup_created_then_event_sent_on_bus(self):
        expected_event = CallPickupCreatedEvent(
            self.call_pickup.id, self.call_pickup.tenant_uuid
        )

        self.notifier.created(self.call_pickup)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_call_pickup_edited_then_event_sent_on_bus(self):
        expected_event = CallPickupEditedEvent(
            self.call_pickup.id, self.call_pickup.tenant_uuid
        )

        self.notifier.edited(self.call_pickup)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_call_pickup_deleted_then_event_sent_on_bus(self):
        expected_event = CallPickupDeletedEvent(
            self.call_pickup.id, self.call_pickup.tenant_uuid
        )

        self.notifier.deleted(self.call_pickup)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_call_pickup_deleted_then_sysconfd_event(self):
        self.notifier.deleted(self.call_pickup)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
