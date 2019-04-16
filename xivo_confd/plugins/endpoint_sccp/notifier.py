# -*- coding: utf-8 -*-
# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_sccp.event import (
    CreateSccpEndpointEvent,
    DeleteSccpEndpointEvent,
    EditSccpEndpointEvent,
)

from xivo_confd import bus, sysconfd


class SccpEndpointNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload chan_sccp.so', 'dialplan reload'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, line):
        event = CreateSccpEndpointEvent(line.id)
        self.bus.send_bus_event(event)

    def edited(self, line):
        self.send_sysconfd_handlers()
        event = EditSccpEndpointEvent(line.id)
        self.bus.send_bus_event(event)

    def deleted(self, line):
        self.send_sysconfd_handlers()
        event = DeleteSccpEndpointEvent(line.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return SccpEndpointNotifier(sysconfd, bus)
