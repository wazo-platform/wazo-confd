# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.incall.event import (
    CreateIncallEvent,
    DeleteIncallEvent,
    EditIncallEvent,
)

from xivo_confd import bus


class IncallNotifier:

    def __init__(self, bus):
        self.bus = bus

    def created(self, incall):
        event = CreateIncallEvent(incall.id)
        self.bus.send_bus_event(event)

    def edited(self, incall):
        event = EditIncallEvent(incall.id)
        self.bus.send_bus_event(event)

    def deleted(self, incall):
        event = DeleteIncallEvent(incall.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return IncallNotifier(bus)
