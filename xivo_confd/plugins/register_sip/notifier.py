# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.register.event import (
    CreateRegisterSIPEvent,
    DeleteRegisterSIPEvent,
    EditRegisterSIPEvent,
)

from xivo_confd import bus, sysconfd


class RegisterSIPNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, register):
        self.send_sysconfd_handlers()
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
