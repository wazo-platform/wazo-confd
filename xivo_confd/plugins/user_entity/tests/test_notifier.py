# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock

from xivo_bus.resources.user_entity.event import UserEntityAssociatedEvent
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserEntityNotifier


class TestEntityNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.entity = Mock(id='1')
        self.user = Mock(User, uuid='abcd-1234')

        self.notifier = UserEntityNotifier(self.bus)

    def test_when_entity_associate_to_user_then_event_sent_on_bus(self):
        expected_event = UserEntityAssociatedEvent(self.user.uuid, self.entity.id)

        self.notifier.associated(self.user, self.entity)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
