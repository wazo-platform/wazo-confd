# Copyright 2017-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.register.event import (
    RegisterIAXCreatedEvent,
    RegisterIAXDeletedEvent,
    RegisterIAXEditedEvent,
)

from ..notifier import RegisterIAXNotifier

EXPECTED_SYSCONFD_HANDLERS = {'ipbx': ['iax2 reload']}


class TestRegisterIAXNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.register_iax = Mock(id=1234)

        self.notifier = RegisterIAXNotifier(self.bus, self.sysconfd)

    def test_when_register_iax_created_then_event_sent_on_bus(self):
        expected_event = RegisterIAXCreatedEvent(self.register_iax.id)

        self.notifier.created(self.register_iax)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_register_iax_edited_then_event_sent_on_bus(self):
        expected_event = RegisterIAXEditedEvent(self.register_iax.id)

        self.notifier.edited(self.register_iax)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_register_iax_deleted_then_event_sent_on_bus(self):
        expected_event = RegisterIAXDeletedEvent(self.register_iax.id)

        self.notifier.deleted(self.register_iax)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_register_iax_created_then_iax_reloaded(self):
        self.notifier.created(self.register_iax)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )

    def test_when_register_iax_edited_then_iax_reloaded(self):
        self.notifier.edited(self.register_iax)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )

    def test_when_register_iax_deleted_then_iax_reloaded(self):
        self.notifier.deleted(self.register_iax)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )
