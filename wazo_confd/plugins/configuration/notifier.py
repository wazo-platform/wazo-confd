# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.configuration.event import LiveReloadEditedEvent

from wazo_confd import bus


class LiveReloadNotifier:

    def __init__(self, bus):
        self.bus = bus

    def edited(self, live_reload):
        event = LiveReloadEditedEvent(live_reload['enabled'])
        self.bus.send_bus_event(event)


def build_notifier():
    return LiveReloadNotifier(bus)
