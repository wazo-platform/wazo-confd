# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.iax_callnumberlimits.event import EditIAXCallNumberLimitsEvent
from xivo_dao.alchemy.iaxcallnumberlimits import IAXCallNumberLimits

from ..notifier import IAXCallNumberLimitsNotifier

SYSCONFD_HANDLERS = {
    'ipbx': ['iax2 reload'],
    'agentbus': [],
}


class TestIAXCallNumberLimitsNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.iax_callnumberlimits = Mock(IAXCallNumberLimits)
        self.sysconfd = Mock()

        self.notifier = IAXCallNumberLimitsNotifier(self.bus, self.sysconfd)

    def test_when_iax_callnumberlimits_edited_then_event_sent_on_bus(self):
        expected_event = EditIAXCallNumberLimitsEvent()

        self.notifier.edited(self.iax_callnumberlimits)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_iax_callnumberlimits_edited_then_iax_reloaded(self):
        self.notifier.edited(self.iax_callnumberlimits)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
