# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.skill.event import (
    SkillCreatedEvent,
    SkillDeletedEvent,
    SkillEditedEvent,
)

from wazo_confd import bus


class SkillNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, skill):
        event = SkillCreatedEvent(skill.id, skill.tenant_uuid)
        self.bus.send_bus_event(event)

    def edited(self, skill):
        event = SkillEditedEvent(skill.id, skill.tenant_uuid)
        self.bus.send_bus_event(event)

    def deleted(self, skill):
        event = SkillDeletedEvent(skill.id, skill.tenant_uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return SkillNotifier(bus)
