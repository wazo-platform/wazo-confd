# Copyright 2019-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.hep.event import HEPGeneralEditedEvent

from wazo_confd import bus, sysconfd


class HEPConfigurationNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, hep):
        if section_name == 'general':
            event = HEPGeneralEditedEvent()
            self.bus.queue_event(event)

        self.send_sysconfd_handlers(['module reload res_hep.so'])


def build_notifier():
    return HEPConfigurationNotifier(bus, sysconfd)
