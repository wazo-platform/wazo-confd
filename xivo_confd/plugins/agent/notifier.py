# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.agent.event import (
    CreateAgentEvent,
    DeleteAgentEvent,
    EditAgentEvent,
)

from xivo_confd import bus


class AgentNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, agent):
        # TODO ctibus event
        event = CreateAgentEvent(agent.id)
        self.bus.send_bus_event(event)

    def edited(self, agent):
        event = EditAgentEvent(agent.id)
        self.bus.send_bus_event(event)

    def deleted(self, agent):
        event = DeleteAgentEvent(agent.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return AgentNotifier(bus)
