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
        event = PagingCallerUsersAssociatedEvent(paging.id, user_uuids)
        headers = self._build_headers(paging)
        self.bus.send_bus_event(event, headers=headers)

    def members_associated(self, paging, users):
        user_uuids = [user.uuid for user in users]
        event = PagingMemberUsersAssociatedEvent(paging.id, user_uuids)
        headers = self._build_headers(paging)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, paging):
        return {'tenant_uuid': str(paging.tenant_uuid)}


def build_notifier():
    return PagingUserNotifier(bus)
