# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.user.event import UserFallbackEditedEvent

from wazo_confd import bus


class UserFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, user):
        event = UserFallbackEditedEvent(user.id, user.tenant_uuid, user.uuid)
        self.bus.queue_event(event)


def build_notifier():
    return UserFallbackNotifier(bus)
