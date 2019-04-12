# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.ivr.event import (
    CreateIvrEvent,
    DeleteIvrEvent,
    EditIvrEvent,
)

from xivo_confd import bus, sysconfd


class IvrNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['dialplan reload'],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, ivr):
        self.send_sysconfd_handlers()
        event = CreateIvrEvent(ivr.id)
        self.bus.send_bus_event(event)

    def edited(self, ivr):
        self.send_sysconfd_handlers()
        event = EditIvrEvent(ivr.id)
        self.bus.send_bus_event(event)

    def deleted(self, ivr):
        self.send_sysconfd_handlers()
        event = DeleteIvrEvent(ivr.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return IvrNotifier(bus, sysconfd)
