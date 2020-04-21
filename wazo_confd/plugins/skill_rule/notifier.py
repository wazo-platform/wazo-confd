# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.skill_rule.event import (
    CreateSkillRuleEvent,
    DeleteSkillRuleEvent,
    EditSkillRuleEvent,
)

from wazo_confd import bus, sysconfd


class SkillRuleNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, skill_rule):
        self.send_sysconfd_handlers()
        event = CreateSkillRuleEvent(skill_rule.id)
        self.bus.send_bus_event(event)

    def edited(self, skill_rule):
        self.send_sysconfd_handlers()
        event = EditSkillRuleEvent(skill_rule.id)
        self.bus.send_bus_event(event)

    def deleted(self, skill_rule):
        self.send_sysconfd_handlers()
        event = DeleteSkillRuleEvent(skill_rule.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return SkillRuleNotifier(bus, sysconfd)
