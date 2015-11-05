# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_bus.resources.endpoint_sccp.event import CreateSccpEndpointEvent, \
    EditSccpEndpointEvent, DeleteSccpEndpointEvent

from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_confd.plugins.endpoint_sccp.notifier import SccpEndpointNotifier

from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint


SYSCONFD_HANDLERS = {'ctibus': [],
                     'dird': [],
                     'ipbx': ['module reload chan_sccp', 'dialplan reload'],
                     'agentbus': []}


class TestSccpEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock(SysconfdPublisher)
        self.bus = Mock()
        self.sccp_endpoint = Mock(SCCPEndpoint, id=1234)

        self.notifier = SccpEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sccp_endpoint_created_then_event_sent_on_bus(self):
        expected_event = CreateSccpEndpointEvent(self.sccp_endpoint.id)

        self.notifier.created(self.sccp_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_sccp_endpoint_edited_then_sccp_reloaded(self):
        self.notifier.edited(self.sccp_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sccp_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = EditSccpEndpointEvent(self.sccp_endpoint.id)

        self.notifier.edited(self.sccp_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_sccp_endpoint_deleted_then_sccp_reloaded(self):
        self.notifier.deleted(self.sccp_endpoint)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sccp_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteSccpEndpointEvent(self.sccp_endpoint.id)

        self.notifier.deleted(self.sccp_endpoint)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
