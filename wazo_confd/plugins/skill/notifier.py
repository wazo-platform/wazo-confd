# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.skill.event import (
    CreateSkillEvent,
    DeleteSkillEvent,
    EditSkillEvent,
)

from wazo_confd import bus


class SkillNotifier:

    def __init__(self, bus):
        self.bus = bus

    def created(self, skill):
        event = CreateSkillEvent(skill.id)
        self.bus.send_bus_event(event)

    def edited(self, skill):
        event = EditSkillEvent(skill.id)
        self.bus.send_bus_event(event)

    def deleted(self, skill):
        event = DeleteSkillEvent(skill.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return SkillNotifier(bus)
