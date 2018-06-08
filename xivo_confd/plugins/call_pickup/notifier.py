# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.call_pickup.event import (
    CreateCallPickupEvent,
    DeleteCallPickupEvent,
    EditCallPickupEvent,
)

from xivo_confd import bus


class CallPickupNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, call_pickup):
        event = CreateCallPickupEvent(call_pickup.id)
        self.bus.send_bus_event(event)

    def edited(self, call_pickup):
        event = EditCallPickupEvent(call_pickup.id)
        self.bus.send_bus_event(event)

    def deleted(self, call_pickup):
        event = DeleteCallPickupEvent(call_pickup.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return CallPickupNotifier(bus)
