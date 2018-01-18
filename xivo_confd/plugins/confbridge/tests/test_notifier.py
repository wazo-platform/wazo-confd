# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.confbridge.event import (
    EditConfBridgeWazoDefaultBridgeEvent,
    EditConfBridgeWazoDefaultUserEvent,
)

from ..notifier import ConfBridgeConfigurationNotifier


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['module reload app_confbridge.so'],
                     'agentbus': []}


class TestConfBridgeConfigurationNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.confbridge = Mock()
        self.sysconfd = Mock()

        self.notifier = ConfBridgeConfigurationNotifier(self.bus, self.sysconfd)

    def test_when_confbridge_wazo_default_bridge_edited_then_event_sent_on_bus(self):
        expected_event = EditConfBridgeWazoDefaultBridgeEvent()

        self.notifier.edited('wazo_default_bridge', self.confbridge)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_confbridge_wazo_default_bridge_edited_then_sip_reloaded(self):
        self.notifier.edited('wazo_default_bridge', self.confbridge)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_confuser_wazo_default_user_edited_then_event_sent_on_bus(self):
        expected_event = EditConfBridgeWazoDefaultUserEvent()

        self.notifier.edited('wazo_default_user', self.confbridge)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_confuser_wazo_default_user_edited_then_sip_reloaded(self):
        self.notifier.edited('wazo_default_user', self.confbridge)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
