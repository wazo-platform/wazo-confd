# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_iax.event import (
    CreateIAXEndpointEvent,
    DeleteIAXEndpointEvent,
    EditIAXEndpointEvent,
)

from xivo_confd import bus, sysconfd


class IAXEndpointNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['iax2 reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, line):
        event = CreateIAXEndpointEvent(line.id)
        self.bus.send_bus_event(event)

    def edited(self, line):
        self.send_sysconfd_handlers()
        event = EditIAXEndpointEvent(line.id)
        self.bus.send_bus_event(event)

    def deleted(self, line):
        self.send_sysconfd_handlers()
        event = DeleteIAXEndpointEvent(line.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return IAXEndpointNotifier(sysconfd, bus)
