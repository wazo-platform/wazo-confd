# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.iax_general.event import EditIAXGeneralEvent

from wazo_confd import bus, sysconfd


class IAXGeneralNotifier:

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {
            'ipbx': ipbx,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, iax_general):
        event = EditIAXGeneralEvent()
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['iax2 reload'])


def build_notifier():
    return IAXGeneralNotifier(bus, sysconfd)
