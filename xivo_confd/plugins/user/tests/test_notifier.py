# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest
from mock import Mock

from xivo_bus.resources.user.event import CreateUserEvent, \
    EditUserEvent, DeleteUserEvent

from xivo_confd.helpers.sysconfd_publisher import SysconfdPublisher
from xivo_confd.plugins.user.notifier import UserNotifier

from xivo_dao.alchemy.userfeatures import UserFeatures as User


def sysconfd_handler(action, user_id):
    cti = 'xivo[user,{},{}]'.format(action, user_id)
    return {'ctibus': [cti],
            'dird': [],
            'ipbx': ['dialplan reload',
                     'module reload chan_sccp.so',
                     'module reload app_queue.so',
                     'sip reload'],
            'agentbus': []}


class TestUserNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock(SysconfdPublisher)
        self.bus = Mock()
        self.user = Mock(User, id=1234)

        self.notifier = UserNotifier(self.sysconfd, self.bus)

    def test_when_user_created_then_sip_reloaded(self):
        self.notifier.created(self.user)

        handler = sysconfd_handler('add', self.user.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(handler)

    def test_when_user_created_then_event_sent_on_bus(self):
        expected_event = CreateUserEvent(self.user.id)

        self.notifier.created(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_user_edited_then_sip_reloaded(self):
        self.notifier.edited(self.user)

        handler = sysconfd_handler('edit', self.user.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(handler)

    def test_when_user_edited_then_event_sent_on_bus(self):
        expected_event = EditUserEvent(self.user.id)

        self.notifier.edited(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_user_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.user)

        handler = sysconfd_handler('delete', self.user.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(handler)

    def test_when_user_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteUserEvent(self.user.id)

        self.notifier.deleted(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
