# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.paging_user.event import (
    PagingMemberUsersAssociatedEvent,
    PagingCallerUsersAssociatedEvent,
)

from wazo_confd import bus


class PagingUserNotifier:
    def __init__(self, bus):
        self.bus = bus

    def callers_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingCallerUsersAssociatedEvent(
            paging.id, user_uuids, paging.tenant_uuid
        )
        self.bus.queue_event(event)

    def members_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingMemberUsersAssociatedEvent(
            paging.id, user_uuids, paging.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return PagingUserNotifier(bus)
