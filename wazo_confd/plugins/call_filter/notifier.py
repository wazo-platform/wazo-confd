# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_filter.event import (
    CreateCallFilterEvent,
    DeleteCallFilterEvent,
    EditCallFilterEvent,
)

from wazo_confd import bus


class CallFilterNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, call_filter):
        event = CreateCallFilterEvent(call_filter.id)
        self.bus.send_bus_event(event)

    def edited(self, call_filter):
        event = EditCallFilterEvent(call_filter.id)
        self.bus.send_bus_event(event)

    def deleted(self, call_filter):
        event = DeleteCallFilterEvent(call_filter.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return CallFilterNotifier(bus)
