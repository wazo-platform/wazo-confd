# Copyright 2019-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.dhcp.event import DHCPEditedEvent

from wazo_confd._bus import BusPublisher
from wazo_confd._sysconfd import SysconfdPublisher


class DHCPNotifier:
    def __init__(self, bus, sysconfd):
        self.bus: BusPublisher = bus
        self.sysconfd: SysconfdPublisher = sysconfd

    def edited(self):
        event = DHCPEditedEvent()
        self.bus.queue_event(event)
        self.sysconfd.commonconf_generate()
        self.sysconfd.commonconf_apply()
