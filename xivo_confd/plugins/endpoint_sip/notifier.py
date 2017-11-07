# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.endpoint_sip.event import CreateSipEndpointEvent, \
    EditSipEndpointEvent, DeleteSipEndpointEvent


class SipEndpointNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['sip reload', 'dialplan reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, line):
        event = CreateSipEndpointEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, line):
        self.send_sysconfd_handlers()
        event = EditSipEndpointEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, line):
        self.send_sysconfd_handlers()
        event = DeleteSipEndpointEvent(line.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return SipEndpointNotifier(sysconfd, bus)
