# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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
from xivo_bus.resources.ivr.event import (CreateIvrEvent,
                                          EditIvrEvent,
                                          DeleteIvrEvent)
from xivo_dao.alchemy.ivr import IVR

from ..notifier import IvrNotifier


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['dialplan reload'],
                     'agentbus': []}


class TestIvrNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.ivr = Mock(IVR, id=2)

        self.notifier = IvrNotifier(self.bus, self.sysconfd)

    def test_when_ivr_created_then_event_sent_on_bus(self):
        expected_event = CreateIvrEvent(self.ivr.id)

        self.notifier.created(self.ivr)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_ivr_edited_then_event_sent_on_bus(self):
        expected_event = EditIvrEvent(self.ivr.id)

        self.notifier.edited(self.ivr)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_ivr_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteIvrEvent(self.ivr.id)

        self.notifier.deleted(self.ivr)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
