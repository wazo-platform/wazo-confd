# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall.event import (
    CreateOutcallEvent,
    DeleteOutcallEvent,
    EditOutcallEvent,
)

from xivo_confd import bus


class OutcallNotifier:

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
