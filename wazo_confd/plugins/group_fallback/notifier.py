# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group.event import EditGroupFallbackEvent

from wazo_confd import bus


class GroupFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, group):
        event = EditGroupFallbackEvent(id=group.id, uuid=str(group.uuid))
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, group):
        return {'tenant_uuid': str(group.tenant_uuid)}


def build_notifier():
    return GroupFallbackNotifier(bus)
