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

from xivo_bus.resources.extension.event import (CreateExtensionEvent,
                                                EditExtensionEvent,
                                                DeleteExtensionEvent)

from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_confd.plugins.extension.notifier import ExtensionNotifier

from xivo_dao.resources.extension.model import Extension


class TestExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock(SysconfdPublisher)
        self.bus = Mock()
        self.extension = Mock(Extension, id=1234, exten='1000', context='default')

        self.notifier = ExtensionNotifier(self.sysconfd, self.bus)

    def test_when_extension_created_then_event_sent_on_bus(self):
        expected_event = CreateExtensionEvent(self.extension.id,
                                              self.extension.exten,
                                              self.extension.context)

        self.notifier.created(self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_extension_created_then_dialplan_reloaded(self):
        expected_handlers = {'ctibus': [],
                             'ipbx': ['dialplan reload'],
                             'agentbus': []}
        self.notifier.created(self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_edited_then_handlers_sent(self):
        expected_handlers = {'ctibus': [],
                             'ipbx': ['dialplan reload', 'sip reload', 'module reload chan_sccp.so'],
                             'agentbus': []}
        self.notifier.edited(self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_edited_then_event_sent_on_bus(self):
        expected_event = EditExtensionEvent(self.extension.id,
                                            self.extension.exten,
                                            self.extension.context)

        self.notifier.edited(self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_extension_deleted_then_dialplan_reloaded(self):
        expected_handlers = {'ctibus': [],
                             'ipbx': ['dialplan reload'],
                             'agentbus': []}
        self.notifier.deleted(self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_extension_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteExtensionEvent(self.extension.id,
                                              self.extension.exten,
                                              self.extension.context)

        self.notifier.deleted(self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
