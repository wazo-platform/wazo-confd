# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.sccp_general.event import EditSCCPGeneralEvent
from xivo_dao.alchemy.sccpgeneralsettings import SCCPGeneralSettings

from ..notifier import SCCPGeneralNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['module reload chan_sccp.so'],
    'agentbus': [],
}


class TestSCCPGeneralNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sccp_general = Mock(SCCPGeneralSettings)
        self.sysconfd = Mock()

        self.notifier = SCCPGeneralNotifier(self.bus, self.sysconfd)

    def test_when_sccp_general_edited_then_event_sent_on_bus(self):
        expected_event = EditSCCPGeneralEvent()

        self.notifier.edited(self.sccp_general)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sccp_general_edited_then_sccp_reloaded(self):
        self.notifier.edited(self.sccp_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
