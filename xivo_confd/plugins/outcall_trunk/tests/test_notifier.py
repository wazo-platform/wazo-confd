# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_bus.resources.incall_extension.event import (IncallExtensionAssociatedEvent,
                                                       IncallExtensionDissociatedEvent)
from ..notifier import IncallExtensionNotifier

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['dialplan reload'],
                     'agentbus': []}


class TestIncallExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.incall = Mock(Incall, id=2)

        self.notifier = IncallExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = IncallExtensionAssociatedEvent(self.incall.id, self.extension.id)

        self.notifier.associated(self.incall, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.incall, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = IncallExtensionDissociatedEvent(self.incall.id, self.extension.id)

        self.notifier.dissociated(self.incall, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.incall, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
