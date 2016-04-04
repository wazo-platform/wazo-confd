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

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_confd.plugins.device.model import Device

from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_confd.plugins.line_device.notifier import LineDeviceNotifier


class TestLineDeviceNotifier(unittest.TestCase):

    REQUEST_HANDLERS = {'ipbx': ['module reload chan_sccp.so'],
                        'agentbus': [],
                        'ctibus': []}

    def setUp(self):
        self.sysconfd = Mock(SysconfdPublisher)
        self.line = Mock(Line)
        self.device = Mock(Device)
        self.notifier = LineDeviceNotifier(self.sysconfd)

    def test_given_line_is_not_sccp_when_associated_then_sccp_not_reloaded(self):
        self.line.endpoint = "sip"
        self.notifier.associated(self.line, self.device)

        assert_that(self.sysconfd.exec_request_handlers.call_count, equal_to(0))

    def test_given_line_is_not_sccp_when_dissociated_then_sccp_not_reloaded(self):
        self.line.endpoint = "sip"
        self.notifier.dissociated(self.line, self.device)

        assert_that(self.sysconfd.exec_request_handlers.call_count, equal_to(0))

    def test_given_line_is_sccp_when_associated_then_sccp_reloaded(self):
        self.line.endpoint = "sccp"
        self.notifier.associated(self.line, self.device)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self.REQUEST_HANDLERS)

    def test_given_line_is_sccp_when_dissociated_then_sccp_reloaded(self):
        self.line.endpoint = "sccp"
        self.notifier.dissociated(self.line, self.device)

        self.sysconfd.exec_request_handlers.assert_called_once_with(self.REQUEST_HANDLERS)
