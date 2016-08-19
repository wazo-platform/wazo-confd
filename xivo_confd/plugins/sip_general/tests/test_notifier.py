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

from xivo_bus.resources.sip_general.event import EditSIPGeneralEvent

from xivo_confd.plugins.sip_general.notifier import SIPGeneralNotifier

from xivo_dao.alchemy.staticsip import StaticSIP

SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['sip reload'],
                     'agentbus': []}


class TestSIPGeneralNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sip_general = Mock(StaticSIP)
        self.sysconfd = Mock()

        self.notifier = SIPGeneralNotifier(self.bus, self.sysconfd)

    def test_when_sip_general_edited_then_event_sent_on_bus(self):
        expected_event = EditSIPGeneralEvent()

        self.notifier.edited(self.sip_general)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_sip_general_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
