# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.call_filter_user.event import (
    CallFilterRecipientUsersAssociatedEvent,
    CallFilterSurrogateUsersAssociatedEvent,
)

from wazo_confd import bus


class CallFilterUserNotifier:
    def __init__(self, bus):
        self.bus = bus

    def recipient_users_associated(self, call_filter, users):
        user_uuids = [user.uuid for user in users]
        event = CallFilterRecipientUsersAssociatedEvent(
            call_filter.id, user_uuids, call_filter.tenant_uuid
        )
        self.bus.queue_event(event)

    def surrogate_users_associated(self, call_filter, users):
        user_uuids = [user.uuid for user in users]
        event = CallFilterSurrogateUsersAssociatedEvent(
            call_filter.id, user_uuids, call_filter.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return CallFilterUserNotifier(bus)
