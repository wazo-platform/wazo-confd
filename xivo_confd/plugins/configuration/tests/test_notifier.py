# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.configuration.event import LiveReloadEditedEvent

from ..notifier import LiveReloadNotifier


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

        self.bus.send_bus_event.assert_called_once_with(expected_event)

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
