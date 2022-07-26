# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.agent_skill.event import (
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
        event = AgentSkillAssociatedEvent(skill.id, agent_skill.skill.id)
        headers = self._build_headers(skill)
        self.bus.send_bus_event(event, headers=headers)

    def skill_dissociated(self, skill, agent_skill):
        self.send_sysconfd_handlers()
        event = AgentSkillDissociatedEvent(skill.id, agent_skill.skill.id)
        headers = self._build_headers(skill)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, skill):
        return {'tenant_uuid': str(skill.tenant_uuid)}


def build_notifier():
    return AgentSkillNotifier(bus, sysconfd)
