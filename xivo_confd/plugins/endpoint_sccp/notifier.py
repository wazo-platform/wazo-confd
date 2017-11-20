# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.endpoint_sccp.event import CreateSccpEndpointEvent, \
    EditSccpEndpointEvent, DeleteSccpEndpointEvent


class SccpEndpointNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['module reload chan_sccp.so', 'dialplan reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, line):
        event = CreateSccpEndpointEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, line):
        self.send_sysconfd_handlers()
        event = EditSccpEndpointEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, line):
        self.send_sysconfd_handlers()
        event = DeleteSccpEndpointEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return SccpEndpointNotifier(sysconfd, bus)
