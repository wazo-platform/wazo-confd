# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.agent.event import (
    CreateAgentEvent,
    DeleteAgentEvent,
    EditAgentEvent,
)

from wazo_confd import bus, sysconfd


class AgentNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx_command=None):
        handlers = {'ipbx': [ipbx_command] if ipbx_command else []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, agent):
        ipbx_command = 'module reload app_queue.so'
        self.send_sysconfd_handlers(ipbx_command)
        event = CreateAgentEvent(agent.id)
        headers = self._build_headers(agent)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, agent):
        ipbx_command = 'module reload app_queue.so'
        self.send_sysconfd_handlers(ipbx_command)
        event = EditAgentEvent(agent.id)
        headers = self._build_headers(agent)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, agent):
        ipbx_command = 'module reload app_queue.so'
        self.send_sysconfd_handlers(ipbx_command)
        event = DeleteAgentEvent(agent.id)
        headers = self._build_headers(agent)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, agent):
        return {'tenant_uuid': str(agent.tenant_uuid)}


def build_notifier():
    return AgentNotifier(bus, sysconfd)
