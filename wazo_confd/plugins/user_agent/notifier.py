# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.user_agent.event import (
    UserAgentAssociatedEvent,
    UserAgentDissociatedEvent,
)

from wazo_confd import bus


class UserAgentNotifier:
    def __init__(self, bus):
        self.bus = bus

    def associated(self, user, agent):
        event = UserAgentAssociatedEvent(agent.id, user.tenant_uuid, user.uuid)
        self.bus.queue_event(event)

    def dissociated(self, user, agent):
        event = UserAgentDissociatedEvent(agent.id, user.tenant_uuid, user.uuid)
        self.bus.queue_event(event)


def build_notifier():
    return UserAgentNotifier(bus)
