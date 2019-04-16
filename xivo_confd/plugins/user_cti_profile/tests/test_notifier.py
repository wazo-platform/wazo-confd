# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock
from xivo_bus.resources.user_cti_profile.event import UserCtiProfileEditedEvent

from ..notifier import UserCtiProfileNotifier

USER_ID = 5


class TestUserCtiProfileNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user = Mock(id=USER_ID)

        self.notifier = UserCtiProfileNotifier(self.bus)

    def test_edited_then_bus_event(self):
        expected_event = UserCtiProfileEditedEvent(
            self.user.id,
            self.user.cti_profile_id,
            self.user.cti_enabled,
        )

        self.notifier.edited(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
