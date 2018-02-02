# -*- coding: utf-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_group.event import UserGroupsAssociatedEvent

from xivo_confd import bus, sysconfd


class UserGroupNotifier(object):

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

    def associated(self, user, groups):
        self.send_sysconfd_handlers()
        group_ids = [group.id for group in groups]
        event = UserGroupsAssociatedEvent(user.uuid, group_ids)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserGroupNotifier(bus, sysconfd)
