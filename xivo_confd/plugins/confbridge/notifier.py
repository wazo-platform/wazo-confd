# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.confbridge.event import (
    EditConfBridgeDefaultBridgeEvent,
    EditConfBridgeDefaultUserEvent,
)


class ConfBridgeConfigurationNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, confbridge):
        if section_name == 'default_bridge':
            event = EditConfBridgeDefaultBridgeEvent()
            self.bus.send_bus_event(event)
        elif section_name == 'default_user':
            event = EditConfBridgeDefaultUserEvent()
            self.bus.send_bus_event(event)

        self.send_sysconfd_handlers(['module reload app_confbridge.so'])


def build_notifier():
    return ConfBridgeConfigurationNotifier(bus, sysconfd)
