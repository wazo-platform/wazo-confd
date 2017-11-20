# -*- coding: utf-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.conference_extension.event import (ConferenceExtensionAssociatedEvent,
                                                           ConferenceExtensionDissociatedEvent)
from ..notifier import ConferenceExtensionNotifier

from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.conference import Conference


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['dialplan reload'],
                     'agentbus': []}


class TestConferenceExtensionNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.extension = Mock(Extension, id=1)
        self.conference = Mock(Conference, id=2)

        self.notifier = ConferenceExtensionNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = ConferenceExtensionAssociatedEvent(self.conference.id, self.extension.id)

        self.notifier.associated(self.conference, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.conference, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_dissociate_then_bus_event(self):
        expected_event = ConferenceExtensionDissociatedEvent(self.conference.id, self.extension.id)

        self.notifier.dissociated(self.conference, self.extension)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_dissociate_then_sysconfd_event(self):
        self.notifier.dissociated(self.conference, self.extension)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
