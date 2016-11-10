# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from xivo_confd import bus, sysconfd
from xivo_bus.resources.group_member.event import GroupMemberUsersAssociatedEvent


class GroupMemberUserNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['sip reload',
                             'module reload app_queue.so',
                             'module reload chan_sccp.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, group, users):
        self.send_sysconfd_handlers()
        user_uuids = [user.uuid for user in users]
        event = GroupMemberUsersAssociatedEvent(group.id, user_uuids)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return GroupMemberUserNotifier(bus, sysconfd)
