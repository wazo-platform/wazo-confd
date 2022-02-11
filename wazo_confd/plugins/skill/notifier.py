# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
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
        headers = self._build_headers(skill)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, skill):
        event = EditSkillEvent(skill.id)
        headers = self._build_headers(skill)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, skill):
        event = DeleteSkillEvent(skill.id)
        headers = self._build_headers(skill)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, skill):
        return {'tenant_uuid': str(skill.tenant_uuid)}


def build_notifier():
    return SkillNotifier(bus)
