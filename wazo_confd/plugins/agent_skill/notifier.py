# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.agent_skill.event import (
    AgentSkillAssociatedEvent,
    AgentSkillDissociatedEvent,
)

from wazo_confd import bus


class AgentSkillNotifier:
    def __init__(self, bus):
        self.bus = bus

    def skill_associated(self, skill, agent_skill):
        event = AgentSkillAssociatedEvent(skill.id, agent_skill.skill.id)
        self.bus.send_bus_event(event)

    def skill_dissociated(self, skill, agent_skill):
        event = AgentSkillDissociatedEvent(skill.id, agent_skill.skill.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return AgentSkillNotifier(bus)
