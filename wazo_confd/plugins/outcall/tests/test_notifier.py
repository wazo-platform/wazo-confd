# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from xivo_bus.resources.outcall.event import (
    CreateOutcallEvent,
    EditOutcallEvent,
    DeleteOutcallEvent,
)
from xivo_dao.alchemy.outcall import Outcall

from ..notifier import OutcallNotifier


class TestOutcallNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.outcall = Mock(Outcall, id=1234, tenant_uuid=uuid4())
        self.expected_headers = {'tenant_uuid': str(self.outcall.tenant_uuid)}

        self.notifier = OutcallNotifier(self.bus)

    def test_when_outcall_created_then_event_sent_on_bus(self):
        expected_event = CreateOutcallEvent(self.outcall.id)

        self.notifier.created(self.outcall)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_outcall_edited_then_event_sent_on_bus(self):
        expected_event = EditOutcallEvent(self.outcall.id)

        self.notifier.edited(self.outcall)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_outcall_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteOutcallEvent(self.outcall.id)

        self.notifier.deleted(self.outcall)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
