# Copyright 2017-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from wazo_bus.resources.outcall_schedule.event import (
    OutcallScheduleAssociatedEvent,
    OutcallScheduleDissociatedEvent,
)
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.schedule import Schedule

from ..notifier import OutcallScheduleNotifier


class TestOutcallScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(Schedule, id=1)
        self.outcall = Mock(Outcall, id=2, tenant_uuid=uuid4())

        self.notifier = OutcallScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = OutcallScheduleAssociatedEvent(
            self.outcall.id, self.schedule.id, self.outcall.tenant_uuid
        )

        self.notifier.associated(self.outcall, self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_then_bus_event(self):
        expected_event = OutcallScheduleDissociatedEvent(
            self.outcall.id, self.schedule.id, self.outcall.tenant_uuid
        )

        self.notifier.dissociated(self.outcall, self.schedule)

        self.bus.queue_event.assert_called_once_with(expected_event)
