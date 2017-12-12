# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.register.event import (
    CreateRegisterSIPEvent,
    DeleteRegisterSIPEvent,
    EditRegisterSIPEvent,
)


class RegisterSIPNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['sip reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, register):
        event = CreateRegisterSIPEvent(register.id)
        self.bus.send_bus_event(event)

    def edited(self, register):
        self.send_sysconfd_handlers()
        event = EditRegisterSIPEvent(register.id)
        self.bus.send_bus_event(event)

    def deleted(self, register):
        self.send_sysconfd_handlers()
        event = DeleteRegisterSIPEvent(register.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return RegisterSIPNotifier(bus, sysconfd)
