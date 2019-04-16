# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.configuration.event import LiveReloadEditedEvent

from xivo_confd import bus


class LiveReloadNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def edited(self, live_reload):
        event = LiveReloadEditedEvent(live_reload['enabled'])
        self.bus.send_bus_event(event)


def build_notifier():
    return LiveReloadNotifier(bus)
