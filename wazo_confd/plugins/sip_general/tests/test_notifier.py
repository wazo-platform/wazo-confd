# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.sip_general.event import EditSIPGeneralEvent
from xivo_dao.alchemy.staticsip import StaticSIP

from ..notifier import SIPGeneralNotifier


SYSCONFD_HANDLERS = {'ipbx': ['module reload res_pjsip.so'], 'agentbus': []}


class TestSIPGeneralNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sip_general = Mock(StaticSIP)
        self.sysconfd = Mock()

        self.notifier = SIPGeneralNotifier(self.bus, self.sysconfd)

    def test_when_sip_general_edited_then_event_sent_on_bus(self):
        expected_event = EditSIPGeneralEvent()

        self.notifier.edited(self.sip_general)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_sip_general_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip_general)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
