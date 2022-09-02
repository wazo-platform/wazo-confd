# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.agent.event import (
    AgentCreatedEvent,
    AgentDeletedEvent,
    AgentEditedEvent,
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
        event = AgentCreatedEvent(agent.id, agent.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, agent):
        ipbx_command = 'module reload app_queue.so'
        self.send_sysconfd_handlers(ipbx_command)
        event = AgentEditedEvent(agent.id, agent.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, agent):
        ipbx_command = 'module reload app_queue.so'
        self.send_sysconfd_handlers(ipbx_command)
        event = AgentDeletedEvent(agent.id, agent.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return AgentNotifier(bus, sysconfd)
