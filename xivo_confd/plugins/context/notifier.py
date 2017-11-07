# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.context.event import (CreateContextEvent,
                                              EditContextEvent,
                                              DeleteContextEvent)


class ContextNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['dialplan reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, context):
        self.send_sysconfd_handlers()
        event = CreateContextEvent(context.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, context):
        self.send_sysconfd_handlers()
        event = EditContextEvent(context.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, context):
        self.send_sysconfd_handlers()
        event = DeleteContextEvent(context.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return ContextNotifier(bus, sysconfd)
