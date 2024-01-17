# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from uuid import uuid4
from unittest.mock import Mock, call

from wazo_bus.resources.func_key.event import (
    FuncKeyTemplateCreatedEvent,
    FuncKeyTemplateDeletedEvent,
    FuncKeyTemplateEditedEvent,
)
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate

from ..notifier import FuncKeyTemplateNotifier

SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload']}
SYSCONFD_HANDLERS_SCCP = {'ipbx': ['module reload chan_sccp.so']}


class TestFuncKeyTemplateNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.func_key_template = Mock(FuncKeyTemplate, id=10, tenant_uuid=str(uuid4()))
        self.expected_headers = {'tenant_uuid': self.func_key_template.tenant_uuid}
        self.notifier = FuncKeyTemplateNotifier(self.bus, self.sysconfd, self.device_db)

    def test_when_func_key_template_created_then_event_sent_on_bus(self):
        expected_event = FuncKeyTemplateCreatedEvent(
            self.func_key_template.id, self.func_key_template.tenant_uuid
        )

        self.notifier.created(self.func_key_template)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_func_key_template_edited_then_event_sent_on_bus(self):
        expected_event = FuncKeyTemplateEditedEvent(
            self.func_key_template.id, self.func_key_template.tenant_uuid
        )

        self.notifier.edited(self.func_key_template, None)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_given_sccp_device_has_funckey_when_func_key_template_edited_then_sccp_reloaded(
        self,
    ):
        self.device_db.template_has_sccp_device.return_value = True

        self.notifier.edited(self.func_key_template, None)

        self.device_db.template_has_sccp_device.assert_called_once_with(
            self.func_key_template.id
        )
        calls = [call(SYSCONFD_HANDLERS), call(SYSCONFD_HANDLERS_SCCP)]
        self.sysconfd.exec_request_handlers.assert_has_calls(calls)

    def test_given_template_has_no_devices_when_edited_then_sccp_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_func_key_template_edited_and_no_change_then_dialplan_not_reloaded(
        self,
    ):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template, [])

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_func_key_template_edited_and_change_then_dialplan_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False
        updated_fields = ['1']

        self.notifier.edited(self.func_key_template, updated_fields)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_func_key_template_edited_and_undefined_change_then_dialplan_reloaded(
        self,
    ):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_func_key_template_deleted_then_event_sent_on_bus(self):
        expected_event = FuncKeyTemplateDeletedEvent(
            self.func_key_template.id, self.func_key_template.tenant_uuid
        )

        self.notifier.deleted(self.func_key_template)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_given_sccp_device_has_funckey_when_func_key_template_deleted_then_sccp_reloaded(
        self,
    ):
        self.device_db.template_has_sccp_device.return_value = True

        self.notifier.deleted(self.func_key_template)

        self.device_db.template_has_sccp_device.assert_called_once_with(
            self.func_key_template.id
        )
        calls = [call(SYSCONFD_HANDLERS), call(SYSCONFD_HANDLERS_SCCP)]
        self.sysconfd.exec_request_handlers.assert_has_calls(calls)

    def test_given_template_has_no_devices_when_deleted_then_sccp_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.deleted(self.func_key_template)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
