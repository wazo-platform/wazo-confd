# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_filter.event import EditCallFilterFallbackEvent

from xivo_confd import bus


class CallFilterFallbackNotifier:

    def __init__(self, bus):
        self.bus = bus

    def edited(self, call_filter):
        event = EditCallFilterFallbackEvent(call_filter.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return CallFilterFallbackNotifier(bus)
