# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.sip_general.event import EditSIPGeneralEvent


class SIPGeneralNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, sip_general):
        event = EditSIPGeneralEvent()
        self.bus.send_bus_event(event, event.routing_key)
        self.send_sysconfd_handlers(['sip reload'])


def build_notifier():
    return SIPGeneralNotifier(bus, sysconfd)
