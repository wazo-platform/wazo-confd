# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user.event import EditUserFallbackEvent

from wazo_confd import bus


class UserFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, user):
        event = EditUserFallbackEvent(user.id, user.uuid)
        headers = self._build_headers(user)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, user):
        return {'tenant_uuid': str(user.tenant_uuid)}


def build_notifier():
    return UserFallbackNotifier(bus)
