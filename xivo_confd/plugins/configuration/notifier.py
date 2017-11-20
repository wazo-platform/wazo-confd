# -*- coding: utf-8 -*-
# Copyright (C) 2013-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.configuration.event import LiveReloadEditedEvent


class LiveReloadNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, cti_commands):
        handlers = {'ctibus': cti_commands,
                    'ipbx': [],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, live_reload):
        event = LiveReloadEditedEvent(live_reload['enabled'])
        self.bus.send_bus_event(event, event.routing_key)
        if live_reload['enabled']:
            self.send_sysconfd_handlers(['xivo[cticonfig,update]'])


def build_notifier():
    return LiveReloadNotifier(bus, sysconfd)
