# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.dhcp.event import EditDHCPEvent


class DHCPNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def edited(self):
        event = EditDHCPEvent()
        self.bus.send_bus_event(event)
        self.sysconfd.commonconf_generate()
        self.sysconfd.commonconf_apply()
