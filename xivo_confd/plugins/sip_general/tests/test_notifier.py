# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

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
