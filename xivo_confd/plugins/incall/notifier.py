# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.incall.event import (CreateIncallEvent,
                                             EditIncallEvent,
                                             DeleteIncallEvent)


class IncallNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, incall):
        event = CreateIncallEvent(incall.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, incall):
        event = EditIncallEvent(incall.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, incall):
        event = DeleteIncallEvent(incall.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return IncallNotifier(bus)
