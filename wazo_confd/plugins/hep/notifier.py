# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.hep.event import HEPGeneralUpdatedEvent

from wazo_confd import bus, sysconfd


class HEPConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, hep):
        if section_name == 'general':
            event = HEPGeneralUpdatedEvent()
            self.bus.send_bus_event(event)

        self.send_sysconfd_handlers(['module reload res_hep.so'])


def build_notifier():
    return HEPConfigurationNotifier(bus, sysconfd)
