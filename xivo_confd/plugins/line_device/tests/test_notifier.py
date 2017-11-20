# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from hamcrest import assert_that, equal_to

from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_confd.plugins.device.model import Device

from xivo_confd.plugins.line_device.notifier import LineDeviceNotifier


class TestLineDeviceNotifier(unittest.TestCase):

    REQUEST_HANDLERS = {'ipbx': ['module reload chan_sccp.so'],
                        'agentbus': [],
                        'ctibus': []}

    def setUp(self):
        self.sysconfd = Mock()
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
