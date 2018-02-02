# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.outcall.event import (
    CreateOutcallEvent,
    DeleteOutcallEvent,
    EditOutcallEvent,
)

from xivo_confd import bus


class OutcallNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, outcall):
        event = CreateOutcallEvent(outcall.id)
        self.bus.send_bus_event(event)

    def edited(self, outcall):
        event = EditOutcallEvent(outcall.id)
        self.bus.send_bus_event(event)

    def deleted(self, outcall):
        event = DeleteOutcallEvent(outcall.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return OutcallNotifier(bus)
