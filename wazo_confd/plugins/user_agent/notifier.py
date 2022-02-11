# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_agent.event import (
    UserAgentAssociatedEvent,
    UserAgentDissociatedEvent,
)

from wazo_confd import bus


class UserAgentNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, agent):
        event = UserAgentAssociatedEvent(user.uuid, agent.id)
        headers = self._build_headers(user)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, user, agent):
        event = UserAgentDissociatedEvent(user.uuid, agent.id)
        headers = self._build_headers(user)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, user):
        return {'tenant_uuid': str(user.tenant_uuid)}


def build_notifier():
    return UserAgentNotifier(bus)
