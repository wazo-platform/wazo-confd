# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.group.event import (CreateGroupEvent,
                                            EditGroupEvent,
                                            DeleteGroupEvent)


class GroupNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['module reload app_queue.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, group):
        self.send_sysconfd_handlers()
        event = CreateGroupEvent(group.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, group):
        self.send_sysconfd_handlers()
        event = EditGroupEvent(group.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, group):
        self.send_sysconfd_handlers()
        event = DeleteGroupEvent(group.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return GroupNotifier(bus, sysconfd)
