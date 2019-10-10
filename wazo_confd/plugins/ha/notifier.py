# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.ha.event import EditHAEvent


class HANotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def edited(self, ha):
        event = EditHAEvent()
        self.bus.send_bus_event(event)
        ha_sysconf = {
            'node_type': ha['node_type'],
            'remote_address': ha.get('remote_address') or '',
        }
        self.sysconfd.update_ha_config(ha_sysconf)
