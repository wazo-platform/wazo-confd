# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import Mock

from xivo_confd.plugins.configuration.notifier import LiveReloadNotifier
from xivo_bus.resources.configuration.event import LiveReloadEditedEvent


class TestLiveReloadNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.live_reload = {'enabled': True}
        self.notifier = LiveReloadNotifier(self.bus, self.sysconfd)

    def test_when_live_reload_edited_then_event_sent_on_bus(self):
        expected_event = LiveReloadEditedEvent(self.live_reload['enabled'])

        self.notifier.edited(self.live_reload)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_live_reload_enabled_then_sysconfd_called(self):
        expected_handlers = {'ctibus': ['xivo[cticonfig,update]'],
                             'ipbx': [],
                             'agentbus': []}
        live_reload = {'enabled': True}

        self.notifier.edited(live_reload)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_live_reload_disabled_then_sysconfd_not_called(self):
        live_reload = {'enabled': False}

        self.notifier.edited(live_reload)

        self.sysconfd.exec_request_handlers.assert_not_called()
