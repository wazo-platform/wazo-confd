# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.skill_rule.event import (
    CreateSkillRuleEvent,
    DeleteSkillRuleEvent,
    EditSkillRuleEvent,
)

from xivo_confd import bus


class SkillRuleNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, skill_rule):
        event = CreateSkillRuleEvent(skill_rule.id)
        self.bus.send_bus_event(event)

    def edited(self, skill_rule):
        event = EditSkillRuleEvent(skill_rule.id)
        self.bus.send_bus_event(event)

    def deleted(self, skill_rule):
        event = DeleteSkillRuleEvent(skill_rule.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return SkillRuleNotifier(bus)
