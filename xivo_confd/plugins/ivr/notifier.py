# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.ivr.event import (CreateIvrEvent,
                                          EditIvrEvent,
                                          DeleteIvrEvent)

from xivo_confd import bus, sysconfd


class IvrNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['dialplan reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, ivr):
        self.send_sysconfd_handlers()
        event = CreateIvrEvent(ivr.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, ivr):
        self.send_sysconfd_handlers()
        event = EditIvrEvent(ivr.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, ivr):
        self.send_sysconfd_handlers()
        event = DeleteIvrEvent(ivr.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return IvrNotifier(bus, sysconfd)
