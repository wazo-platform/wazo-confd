# -*- coding: utf-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest

from mock import Mock

from xivo_bus.resources.user_group.event import UserGroupsAssociatedEvent
from ..notifier import UserGroupNotifier

from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.groupfeatures import GroupFeatures as Group


SYSCONFD_HANDLERS = {'ctibus': [],
                     'ipbx': ['sip reload',
                              'module reload app_queue.so',
                              'module reload chan_sccp.so'],
                     'agentbus': []}


class TestUserGroupNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.group1 = Mock(Group, id=1)
        self.group2 = Mock(Group, id=2)
        self.user = Mock(User, uuid='abcd-1234')

        self.notifier = UserGroupNotifier(self.bus, self.sysconfd)

    def test_associate_then_bus_event(self):
        expected_event = UserGroupsAssociatedEvent(self.user.uuid, [self.group1.id, self.group2.id])

        self.notifier.associated(self.user, [self.group1, self.group2])

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_associate_then_sysconfd_event(self):
        self.notifier.associated(self.user, [self.group1, self.group2])

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
