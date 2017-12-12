# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.context.event import (
    CreateContextEvent,
    DeleteContextEvent,
    EditContextEvent,
)


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
        self.bus.send_bus_event(event)

    def edited(self, context):
        self.send_sysconfd_handlers()
        event = EditContextEvent(context.id)
        self.bus.send_bus_event(event)

    def deleted(self, context):
        self.send_sysconfd_handlers()
        event = DeleteContextEvent(context.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return ContextNotifier(bus, sysconfd)
