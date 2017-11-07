# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

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
