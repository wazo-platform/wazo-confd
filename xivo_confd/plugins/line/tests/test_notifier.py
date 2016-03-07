# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from xivo_bus.resources.line.event import CreateLineEvent, \
    EditLineEvent, DeleteLineEvent

from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_confd.plugins.line.notifier import LineNotifier

from xivo_dao.alchemy.linefeatures import LineFeatures as Line


SYSCONFD_HANDLERS = {'ctibus': [],
                     'dird': [],
                     'ipbx': ['sip reload', 'dialplan reload', 'module reload chan_sccp.so'],
                     'agentbus': []}


class TestLineNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock(SysconfdPublisher)
        self.bus = Mock()
        self.line = Mock(Line, id=1234)

        self.notifier = LineNotifier(self.sysconfd, self.bus)

    def test_when_line_created_then_sip_reloaded(self):
        self.notifier.created(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_created_then_event_sent_on_bus(self):
        expected_event = CreateLineEvent(self.line.id)

        self.notifier.created(self.line)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_line_edited_then_sip_reloaded(self):
        self.notifier.edited(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_edited_then_event_sent_on_bus(self):
        expected_event = EditLineEvent(self.line.id)

        self.notifier.edited(self.line)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_line_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_line_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteLineEvent(self.line.id)

        self.notifier.deleted(self.line)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
