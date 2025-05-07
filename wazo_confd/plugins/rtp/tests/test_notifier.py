# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.rtp.event import (
    RTPGeneralEditedEvent,
    RTPIceHostCandidatesEditedEvent,
)

from ..notifier import RTPConfigurationNotifier

SYSCONFD_HANDLERS = {'ipbx': ['module reload res_rtp_asterisk.so']}


class TestRTPConfigurationNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.rtp = Mock()
        self.sysconfd = Mock()

        self.notifier = RTPConfigurationNotifier(self.bus, self.sysconfd)

    def test_when_rtp_general_edited_then_event_sent_on_bus(self):
        expected_event = RTPGeneralEditedEvent()

        self.notifier.edited('general', self.rtp)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_rtp_general_edited_then_sip_reloaded(self):
        self.notifier.edited('general', self.rtp)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_confuser_ice_host_candidates_edited_then_event_sent_on_bus(self):
        expected_event = RTPIceHostCandidatesEditedEvent()

        self.notifier.edited('ice_host_candidates', self.rtp)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_confuser_ice_host_candidates_edited_then_sip_reloaded(self):
        self.notifier.edited('ice_host_candidates', self.rtp)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
