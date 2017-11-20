# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.line.event import CreateLineEvent, \
    EditLineEvent, DeleteLineEvent


class LineNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['sip reload', 'dialplan reload', 'module reload chan_sccp.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, line):
        self.send_sysconfd_handlers()
        event = CreateLineEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, line, updated_fields):
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers()
        event = EditLineEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, line):
        self.send_sysconfd_handlers()
        event = DeleteLineEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return LineNotifier(sysconfd, bus)
