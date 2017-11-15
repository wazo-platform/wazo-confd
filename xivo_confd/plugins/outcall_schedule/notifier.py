# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.outcall_schedule.event import (OutcallScheduleAssociatedEvent,
                                                      OutcallScheduleDissociatedEvent)


class OutcallScheduleNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, outcall, schedule):
        event = OutcallScheduleAssociatedEvent(outcall.id, schedule.id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, outcall, schedule):
        event = OutcallScheduleDissociatedEvent(outcall.id, schedule.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return OutcallScheduleNotifier(bus)
