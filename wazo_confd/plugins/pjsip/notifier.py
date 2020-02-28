# Copyright 2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.pjsip.event import PJSIPGlobalUpdatedEvent

from wazo_confd import bus, sysconfd


class PJSIPConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, file_):
        if section_name == 'global':
            # TODO(pc-m): Adding the variables to the body would avoid a GET
            # from the Sorcery proxy when we implement it
            event = PJSIPGlobalUpdatedEvent()
            self.bus.send_bus_event(event)

        self.send_sysconfd_handlers(['module reload res_pjsip.so'])


def build_notifier():
    return PJSIPConfigurationNotifier(bus, sysconfd)
