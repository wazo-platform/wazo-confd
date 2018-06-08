# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.conference.event import (
    CreateConferenceEvent,
    DeleteConferenceEvent,
    EditConferenceEvent,
)

from ..notifier import ConferenceNotifier

EXPECTED_HANDLERS = {'ctibus': [],
                     'ipbx': ['module reload app_confbridge.so'],
                     'agentbus': []}


class TestConferenceNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.conference = Mock(id=1234)

        self.notifier = ConferenceNotifier(self.bus, self.sysconfd)

    def test_when_conference_created_then_dialplan_reloaded(self):
        self.notifier.created(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_created_then_event_sent_on_bus(self):
        expected_event = CreateConferenceEvent(self.conference.id)

        self.notifier.created(self.conference)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_conference_edited_then_dialplan_reloaded(self):
        self.notifier.edited(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_edited_then_event_sent_on_bus(self):
        expected_event = EditConferenceEvent(self.conference.id)

        self.notifier.edited(self.conference)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_conference_deleted_then_dialplan_reloaded(self):
        self.notifier.deleted(self.conference)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_conference_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteConferenceEvent(self.conference.id)

        self.notifier.deleted(self.conference)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
