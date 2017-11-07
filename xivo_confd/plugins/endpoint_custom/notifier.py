# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.endpoint_custom.event import CreateCustomEndpointEvent, \
    EditCustomEndpointEvent, DeleteCustomEndpointEvent


class CustomEndpointNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, custom):
        event = CreateCustomEndpointEvent(custom.id, custom.interface)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, custom):
        event = EditCustomEndpointEvent(custom.id, custom.interface)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, custom):
        event = DeleteCustomEndpointEvent(custom.id, custom.interface)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return CustomEndpointNotifier(bus)
