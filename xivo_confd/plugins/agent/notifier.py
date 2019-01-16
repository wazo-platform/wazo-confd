# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.agent.event import (
    CreateAgentEvent,
    DeleteAgentEvent,
    EditAgentEvent,
)

from xivo_confd import bus, sysconfd


class AgentNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ctibus_command, ipbx_command=None):
        handlers = {'ctibus': [ctibus_command],
                    'ipbx': [ipbx_command] if ipbx_command else [],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, agent):
        ctibus_command = 'xivo[agent,add,{agent_id}]'.format(agent_id=agent.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = CreateAgentEvent(agent.id)
        self.bus.send_bus_event(event)

    def edited(self, agent):
        ctibus_command = 'xivo[agent,edit,{agent_id}]'.format(agent_id=agent.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = EditAgentEvent(agent.id)
        self.bus.send_bus_event(event)

    def deleted(self, agent):
        ctibus_command = 'xivo[agent,delete,{agent_id}]'.format(agent_id=agent.id)
        ipbx_command = 'module reload app_queue.so'
        self.send_sysconfd_handlers(ctibus_command, ipbx_command)
        event = DeleteAgentEvent(agent.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return AgentNotifier(bus, sysconfd)
