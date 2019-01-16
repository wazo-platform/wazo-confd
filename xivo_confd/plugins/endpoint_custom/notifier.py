# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.endpoint_custom.event import (
    CreateCustomEndpointEvent,
    DeleteCustomEndpointEvent,
    EditCustomEndpointEvent,
)

from xivo_confd import bus


class CustomEndpointNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, custom):
        event = CreateCustomEndpointEvent(custom.id, custom.interface)
        self.bus.send_bus_event(event)

    def edited(self, custom):
        event = EditCustomEndpointEvent(custom.id, custom.interface)
        self.bus.send_bus_event(event)

    def deleted(self, custom):
        event = DeleteCustomEndpointEvent(custom.id, custom.interface)
        self.bus.send_bus_event(event)


def build_notifier():
    return CustomEndpointNotifier(bus)
