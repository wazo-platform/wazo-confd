# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.user_call_permission.event import (
    UserCallPermissionAssociatedEvent,
    UserCallPermissionDissociatedEvent,
)

from wazo_confd import bus


class UserCallPermissionNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, call_permission):
        event = UserCallPermissionAssociatedEvent(
            call_permission.id, user.tenant_uuid, user.uuid
        )
        self.bus.queue_event(event)

    def dissociated(self, user, call_permission):
        event = UserCallPermissionDissociatedEvent(
            call_permission.id, user.tenant_uuid, user.uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return UserCallPermissionNotifier(bus)
