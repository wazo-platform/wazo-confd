# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.user.event import UserEditedEvent

from wazo_confd import bus


class UserCallerIDDefaultNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, user):
        event = UserEditedEvent(
            user.id,
            user.uuid,
            user.subscription_type,
            user.created_at,
            user.tenant_uuid,
        )
        self.bus.queue_event(event)


def build_notifier_default():
    return UserCallerIDDefaultNotifier(bus)
