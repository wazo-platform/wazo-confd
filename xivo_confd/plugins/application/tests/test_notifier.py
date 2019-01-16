# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.application.event import (
    CreateApplicationEvent,
    DeleteApplicationEvent,
    EditApplicationEvent,
)

from ..notifier import ApplicationNotifier


class TestApplicationNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.application = Mock(uuid='1234-abcd')

        self.notifier = ApplicationNotifier(self.bus)

    def test_when_application_created_then_event_sent_on_bus(self):
        expected_event = CreateApplicationEvent(self.application.uuid)

        self.notifier.created(self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_application_edited_then_event_sent_on_bus(self):
        expected_event = EditApplicationEvent(self.application.uuid)

        self.notifier.edited(self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_application_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteApplicationEvent(self.application.uuid)

        self.notifier.deleted(self.application)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
