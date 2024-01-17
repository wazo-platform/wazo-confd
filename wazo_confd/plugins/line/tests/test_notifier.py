# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from wazo_bus.resources.line.event import (
    LineCreatedEvent,
    LineDeletedEvent,
    LineEditedEvent,
)
from xivo_dao.alchemy.linefeatures import LineFeatures as Line

from ..notifier import LineNotifier

SYSCONFD_HANDLERS = {
    'ipbx': [
        'module reload res_pjsip.so',
        'dialplan reload',
        'module reload chan_sccp.so',
    ]
}


class TestLineNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.line = Mock(Line, id=1234, protocol='sip', tenant_uuid=uuid4())
        self.line.name = 'limitation of mock instantiation with name ...'
        self.line_serialized = {
            'id': self.line.id,
            'name': self.line.name,
            'tenant_uuid': str(self.line.tenant_uuid),
            'protocol': self.line.protocol,
        }

        self.notifier = LineNotifier(self.sysconfd, self.bus)

    def test_when_line_created_then_sip_reloaded(self):
        self.notifier.created(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_created_then_event_sent_on_bus(self):
        expected_event = LineCreatedEvent(self.line_serialized, self.line.tenant_uuid)

        self.notifier.created(self.line)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_line_edited_then_sip_reloaded(self):
        updated_fields = ['name']
        self.notifier.edited(self.line, updated_fields)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_edited_and_undefined_change_then_sip_reloaded(self):
        self.notifier.edited(self.line, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_edited_and_no_change_then_sip_not_reloaded(self):
        updated_fields = []
        self.notifier.edited(self.line, updated_fields)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_line_edited_then_event_sent_on_bus(self):
        expected_event = LineEditedEvent(self.line_serialized, self.line.tenant_uuid)

        self.notifier.edited(self.line, None)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_line_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_deleted_then_event_sent_on_bus(self):
        expected_event = LineDeletedEvent(self.line_serialized, self.line.tenant_uuid)

        self.notifier.deleted(self.line)

        self.bus.queue_event.assert_called_once_with(expected_event)
