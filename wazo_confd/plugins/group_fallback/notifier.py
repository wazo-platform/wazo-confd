# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group.event import GroupFallbackEditedEvent

from wazo_confd import bus


class GroupFallbackNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, group):
        event = GroupFallbackEditedEvent(group.id, group.uuid, group.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return GroupFallbackNotifier(bus)
