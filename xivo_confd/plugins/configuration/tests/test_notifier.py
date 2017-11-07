# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_confd.plugins.configuration.notifier import LiveReloadNotifier
from xivo_bus.resources.configuration.event import LiveReloadEditedEvent


class TestLiveReloadNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.device_db = Mock()
        self.live_reload = {'enabled': True}
        self.notifier = LiveReloadNotifier(self.bus, self.sysconfd)

    def test_when_live_reload_edited_then_event_sent_on_bus(self):
        expected_event = LiveReloadEditedEvent(self.live_reload['enabled'])

        self.notifier.edited(self.live_reload)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_live_reload_enabled_then_sysconfd_called(self):
        expected_handlers = {'ctibus': ['xivo[cticonfig,update]'],
                             'ipbx': [],
                             'agentbus': []}
        live_reload = {'enabled': True}

        self.notifier.edited(live_reload)

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected_handlers)

    def test_when_live_reload_disabled_then_sysconfd_not_called(self):
        live_reload = {'enabled': False}

        self.notifier.edited(live_reload)

        self.sysconfd.exec_request_handlers.assert_not_called()
