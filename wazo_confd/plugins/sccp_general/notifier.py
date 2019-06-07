# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.sccp_general.event import EditSCCPGeneralEvent

from wazo_confd import bus, sysconfd


class SCCPGeneralNotifier:

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {
            'ipbx': ipbx,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, sccp_general):
        event = EditSCCPGeneralEvent()
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['module reload chan_sccp.so'])


def build_notifier():
    return SCCPGeneralNotifier(bus, sysconfd)
