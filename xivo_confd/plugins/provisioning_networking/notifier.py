# -*- coding: utf-8 -*-
# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.provisioning_networking.event import (
    EditProvisioningNetworkingEvent,
)


class ProvisioningNetworkingNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def edited(self, provisioning_networking):
        event = EditProvisioningNetworkingEvent()
        self.bus.send_bus_event(event)
        self.sysconfd.restart_provd()
