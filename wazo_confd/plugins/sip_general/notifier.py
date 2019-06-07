# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.sip_general.event import EditSIPGeneralEvent

from xivo_confd import bus, sysconfd


class SIPGeneralNotifier:

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {
            'ipbx': ipbx,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, sip_general):
        event = EditSIPGeneralEvent()
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['module reload res_pjsip.so'])


def build_notifier():
    return SIPGeneralNotifier(bus, sysconfd)
