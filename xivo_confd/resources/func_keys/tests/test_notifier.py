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
from mock import Mock

from xivo_dao.resources.func_key_template.model import FuncKeyTemplate

from xivo_bus.resources.func_key.event import CreateFuncKeyTemplateEvent, \
    EditFuncKeyTemplateEvent, DeleteFuncKeyTemplateEvent

from xivo_confd.helpers.bus_publisher import BusPublisher
from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_confd.resources.func_keys.notifier import FuncKeyTemplateNotifier


class TestFuncKeyTemplateNotifier(unittest.TestCase):

    REQUEST_HANDLERS = {'dird': [],
                        'ipbx': ['module reload chan_sccp.so'],
                        'agentbus': [],
                        'ctibus': []}

    def setUp(self):
        self.bus = Mock(BusPublisher)
        self.sysconfd = Mock(SysconfdPublisher)
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

        self.notifier.edited(self.func_key_template)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_given_sccp_device_has_funckey_when_func_key_template_edited_then_sccp_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = True

        self.notifier.edited(self.func_key_template)

        self.device_db.template_has_sccp_device.assert_called_once_with(self.func_key_template.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(self.REQUEST_HANDLERS)

    def test_given_template_has_no_devices_when_edited_then_sccp_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.edited(self.func_key_template)

        self.assertEquals(self.sysconfd.exec_request_handlers.call_count, 0)

    def test_when_func_key_template_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteFuncKeyTemplateEvent(self.func_key_template.id)

        self.notifier.deleted(self.func_key_template)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_given_sccp_device_has_funckey_when_func_key_template_deleted_then_sccp_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = True

        self.notifier.deleted(self.func_key_template)

        self.device_db.template_has_sccp_device.assert_called_once_with(self.func_key_template.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(self.REQUEST_HANDLERS)

    def test_given_template_has_no_devices_when_deleted_then_sccp_not_reloaded(self):
        self.device_db.template_has_sccp_device.return_value = False

        self.notifier.deleted(self.func_key_template)

        self.assertEquals(self.sysconfd.exec_request_handlers.call_count, 0)
