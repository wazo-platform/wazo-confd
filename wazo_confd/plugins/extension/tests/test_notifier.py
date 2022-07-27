# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock

from xivo_bus.resources.extension.event import (
    CreateExtensionEvent,
    DeleteExtensionEvent,
    EditExtensionEvent,
)
from xivo_dao.alchemy.extension import Extension

from ..notifier import ExtensionNotifier


class TestExtensionNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.extension = Mock(
            Extension,
            id=1234,
            exten='1000',
            context='default',
            tenant_uuid=str(uuid4()),
        )
        self.expected_headers = {'tenant_uuid': self.extension.tenant_uuid}

        self.notifier = ExtensionNotifier(self.sysconfd, self.bus)

    def test_when_extension_created_then_event_sent_on_bus(self):
        expected_event = CreateExtensionEvent(
            self.extension.id, self.extension.exten, self.extension.context
        )

        self.notifier.created(self.extension)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_extension_created_then_dialplan_reloaded(self):
        expected_handlers = {'ipbx': ['dialplan reload']}
        self.notifier.created(self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_edited_then_handlers_sent(self):
        expected_handlers = {
            'ipbx': [
                'dialplan reload',
                'module reload res_pjsip.so',
                'module reload chan_sccp.so',
                'module reload app_queue.so',
            ]
        }
        updated_fields = ['exten']
        self.notifier.edited(self.extension, updated_fields)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_edited_and_undefined_change_then_handlers_sent(self):
        expected_handlers = {
            'ipbx': [
                'dialplan reload',
                'module reload res_pjsip.so',
                'module reload chan_sccp.so',
                'module reload app_queue.so',
            ]
        }
        self.notifier.edited(self.extension, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_edited_and_no_change_then_handlers_not_sent(self):
        updated_fields = []
        self.notifier.edited(self.extension, updated_fields)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_extension_edited_then_event_sent_on_bus(self):
        expected_event = EditExtensionEvent(
            self.extension.id, self.extension.exten, self.extension.context
        )

        self.notifier.edited(self.extension, None)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_extension_deleted_then_dialplan_reloaded(self):
        expected_handlers = {'ipbx': ['dialplan reload']}
        self.notifier.deleted(self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteExtensionEvent(
            self.extension.id, self.extension.exten, self.extension.context
        )

        self.notifier.deleted(self.extension)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )
