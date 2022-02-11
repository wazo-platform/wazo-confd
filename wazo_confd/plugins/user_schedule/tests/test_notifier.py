# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from mock import Mock

from xivo_bus.resources.user_schedule.event import (
    UserScheduleAssociatedEvent,
    UserScheduleDissociatedEvent,
)

from ..notifier import UserScheduleNotifier


TENANT_UUID = str(uuid4())


class TestUserScheduleNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schedule = Mock(id=1)
        self.user = Mock(id=2, tenant_uuid=TENANT_UUID)
        self.expected_headers = {'tenant_uuid': TENANT_UUID}

        self.notifier = UserScheduleNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = UserScheduleAssociatedEvent(self.user.id, self.schedule.id)

        self.notifier.associated(self.user, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_dissociate_then_bus_event(self):
        expected_event = UserScheduleDissociatedEvent(self.user.id, self.schedule.id)

        self.notifier.dissociated(self.user, self.schedule)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
