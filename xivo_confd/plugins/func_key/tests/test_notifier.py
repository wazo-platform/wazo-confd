# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


import unittest
from mock import Mock, call

from xivo_dao.resources.func_key_template.model import FuncKeyTemplate

from xivo_bus.resources.func_key.event import (CreateFuncKeyTemplateEvent,
                                               DeleteFuncKeyTemplateEvent,
                                               EditFuncKeyTemplateEvent)

from xivo_confd.plugins.func_key.notifier import FuncKeyTemplateNotifier


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['dialplan reload'],
                     'agentbus': []}
SYSCONFD_HANDLERS_SCCP = {'ctibus': [],
                          'ipbx': ['module reload chan_sccp.so'],
                          'agentbus': []}


class TestFuncKeyTemplateNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.func_key_template = Mock(FuncKeyTemplate, id=10)
        self.notifier = FuncKeyTemplateNotifier(self.bus, self.sysconfd, self.device_db)

    def test_when_func_key_template_created_then_event_sent_on_bus(self):
        expected_event = CreateFuncKeyTemplateEvent(self.func_key_template.id)

        self.notifier.created(self.func_key_template)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_func_key_template_edited_then_event_sent_on_bus(self):
        expected_event = EditFuncKeyTemplateEvent(self.func_key_template.id)

        self.notifier.edited(self.func_key_template, None)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_given_sccp_device_has_funckey_when_func_key_template_edited_then_sccp_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = True

        self.notifier.edited(self.func_key_template, None)

        self.device_db.template_has_sccp_device.assert_called_once_with(self.func_key_template.id)
        calls = [call(SYSCONFD_HANDLERS), call(SYSCONFD_HANDLERS_SCCP)]
        self.sysconfd.exec_request_handlers.assert_has_calls(calls)

    def test_given_template_has_no_devices_when_edited_then_sccp_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_func_key_template_edited_and_no_change_then_dialplan_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template, [])

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_when_func_key_template_edited_and_change_then_dialplan_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False
        updated_fields = ['1']

        self.notifier.edited(self.func_key_template, updated_fields)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_func_key_template_edited_and_undefined_change_then_dialplan_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template, None)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_func_key_template_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteFuncKeyTemplateEvent(self.func_key_template.id)

        self.notifier.deleted(self.func_key_template)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_given_sccp_device_has_funckey_when_func_key_template_deleted_then_sccp_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = True

        self.notifier.deleted(self.func_key_template)

        self.device_db.template_has_sccp_device.assert_called_once_with(self.func_key_template.id)
        calls = [call(SYSCONFD_HANDLERS), call(SYSCONFD_HANDLERS_SCCP)]
        self.sysconfd.exec_request_handlers.assert_has_calls(calls)

    def test_given_template_has_no_devices_when_deleted_then_sccp_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.deleted(self.func_key_template)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
