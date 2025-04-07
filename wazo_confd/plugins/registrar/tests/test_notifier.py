# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.registrar.event import (
    RegistrarCreatedEvent,
    RegistrarDeletedEvent,
    RegistrarEditedEvent,
)

from ..model import Registrar
from ..notifier import RegistrarNotifier
from ..schema import RegistrarSchema


class TestRegistrarNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.schema = RegistrarSchema(exclude=['links'])
        self.registrar = Registrar.from_args(id='1234', name='base')
        self.notifier = RegistrarNotifier(self.bus)

    def test_when_registrar_created_then_event_sent_on_bus(self):
        expected_event = RegistrarCreatedEvent(self.schema.dump(self.registrar))

        self.notifier.created(self.registrar)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_registrar_edited_then_event_sent_on_bus(self):
        expected_event = RegistrarEditedEvent(self.schema.dump(self.registrar))

        self.notifier.edited(self.registrar)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_registrar_deleted_then_event_sent_on_bus(self):
        expected_event = RegistrarDeletedEvent(self.schema.dump(self.registrar))

        self.notifier.deleted(self.registrar)

        self.bus.queue_event.assert_called_once_with(expected_event)
