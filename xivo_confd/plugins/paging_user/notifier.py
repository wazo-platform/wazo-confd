# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.paging_user.event import (
    PagingMemberUsersAssociatedEvent,
    PagingCallerUsersAssociatedEvent,
)

from xivo_confd import bus


class PagingUserNotifier:

    def __init__(self, bus):
        self.bus = bus

    def callers_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingCallerUsersAssociatedEvent(paging.id, user_uuids)
        self.bus.send_bus_event(event)

    def members_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingMemberUsersAssociatedEvent(paging.id, user_uuids)
        self.bus.send_bus_event(event)


def build_notifier():
    return PagingUserNotifier(bus)
