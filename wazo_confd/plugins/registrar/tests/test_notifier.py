# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.registrar.event import (
    CreateRegistrarEvent,
    DeleteRegistrarEvent,
    EditRegistrarEvent,
)

from ..notifier import RegistrarNotifier
from ..model import Registrar


class TestRegistrarNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.registrar = Mock(Registrar, registrar={'id': '1234', 'displayname': 'base'})
        self.notifier = RegistrarNotifier(self.bus)

    def test_when_registrar_created_then_event_sent_on_bus(self):
        expected_event = CreateRegistrarEvent(self.registrar.registrar)

        self.notifier.created(self.registrar)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_registrar_edited_then_event_sent_on_bus(self):
        expected_event = EditRegistrarEvent(self.registrar.registrar)

        self.notifier.edited(self.registrar)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_registrar_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteRegistrarEvent(self.registrar.registrar)

        self.notifier.deleted(self.registrar)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
