# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.agent_skill.event import (
    AgentSkillAssociatedEvent,
    AgentSkillDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class AgentSkillNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_queue.so']}
        self.sysconfd.exec_request_handlers(handlers)

    def skill_associated(self, skill, agent_skill):
        self.send_sysconfd_handlers()
        event = AgentSkillAssociatedEvent(
            skill.id, agent_skill.skill.id, skill.tenant_uuid
        )
        self.bus.queue_event(event)

    def skill_dissociated(self, skill, agent_skill):
        self.send_sysconfd_handlers()
        event = AgentSkillDissociatedEvent(
            skill.id, agent_skill.skill.id, skill.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return AgentSkillNotifier(bus, sysconfd)
