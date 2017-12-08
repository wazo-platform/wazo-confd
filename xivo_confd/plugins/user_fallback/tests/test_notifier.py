# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.user.event import EditUserFallbackEvent
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserFallbackNotifier


class TestUserFallbackNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user = Mock(User, id=1, uuid='abcd-1234')

        self.notifier = UserFallbackNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = EditUserFallbackEvent(self.user.id, self.user.uuid)

        self.notifier.edited(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
