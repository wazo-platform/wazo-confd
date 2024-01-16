# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.switchboard.event import SwitchboardMemberUserAssociatedEvent
from wazo_confd import bus


class SwitchboardMemberUserNotifier:
    def __init__(self, bus):
        self.bus = bus

    def members_associated(self, switchboard, users):
        user_uuids = [user.uuid for user in users]
        event = SwitchboardMemberUserAssociatedEvent(
            switchboard.uuid, switchboard.tenant_uuid, user_uuids
        )
        self.bus.queue_event(event)


def build_notifier():
    return SwitchboardMemberUserNotifier(bus)
