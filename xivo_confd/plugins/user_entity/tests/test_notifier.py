# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.user_entity.event import UserEntityAssociatedEvent
from xivo_confd.plugins.user_entity.notifier import UserEntityNotifier

from xivo_dao.alchemy.userfeatures import UserFeatures as User


class TestEntityNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.entity = Mock(id='1')
        self.user = Mock(User, uuid='abcd-1234')

        self.notifier = UserEntityNotifier(self.bus)

    def test_when_entity_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserEntityAssociatedEvent(self.user.uuid, self.entity.id)

        self.notifier.associated(self.user, self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
