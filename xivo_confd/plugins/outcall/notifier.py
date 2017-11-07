# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.outcall.event import (CreateOutcallEvent,
                                              EditOutcallEvent,
                                              DeleteOutcallEvent)


class OutcallNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, outcall):
        event = CreateOutcallEvent(outcall.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, outcall):
        event = EditOutcallEvent(outcall.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, outcall):
        event = DeleteOutcallEvent(outcall.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return OutcallNotifier(bus)
