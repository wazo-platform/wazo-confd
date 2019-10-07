# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user.event import EditUserFallbackEvent

from wazo_confd import bus


class UserFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, user):
        event = EditUserFallbackEvent(user.id, user.uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserFallbackNotifier(bus)
