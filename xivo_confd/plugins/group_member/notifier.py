# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.group_member.event import (
    GroupMemberUsersAssociatedEvent,
    GroupMemberExtensionsAssociatedEvent,
)

from xivo_confd import bus, sysconfd


class GroupMemberNotifier(object):

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

    def users_associated(self, group, users):
        self.send_sysconfd_handlers()
        user_uuids = [user.uuid for user in users]
        event = GroupMemberUsersAssociatedEvent(group.id, user_uuids)
        self.bus.send_bus_event(event)

    def extensions_associated(self, group, extensions):
        self.send_sysconfd_handlers()
        event = GroupMemberExtensionsAssociatedEvent(group.id, extensions)
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupMemberNotifier(bus, sysconfd)
