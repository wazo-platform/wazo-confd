# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.queue_member.event import (
    QueueMemberAgentAssociatedEvent,
    QueueMemberAgentDissociatedEvent,
    QueueMemberUserAssociatedEvent,
    QueueMemberUserDissociatedEvent,
)
from xivo_bus.resources.agent.event import EditAgentEvent
from wazo_confd import bus, sysconfd


class QueueMemberNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    @staticmethod
    def _build_headers(**kwargs):
        headers = {}
        for key, value in kwargs.items():
            if value:
                headers[key] = value
        return headers

    def _send_agent_edited(self, agent):
        event = EditAgentEvent(agent.id)
        headers = self._build_headers(tenant_uuid=str(agent.tenant_uuid))
        self.bus.send_bus_event(event, headers=headers)

    def send_sysconfd_handlers(self, ipbx_command=[]):
        handlers = {'ipbx': ipbx_command}
        self.sysconfd.exec_request_handlers(handlers)

    def agent_associated(self, queue, member):
        event = QueueMemberAgentAssociatedEvent(
            queue.id, member.agent.id, member.penalty
        )
        headers = self._build_headers(tenant_uuid=str(queue.tenant_uuid))
        self.bus.send_bus_event(event, headers=headers)
        self._send_agent_edited(member.agent)

    def agent_dissociated(self, queue, member):
        event = QueueMemberAgentDissociatedEvent(queue.id, member.agent.id)
        headers = self._build_headers(tenant_uuid=str(queue.tenant_uuid))
        self.bus.send_bus_event(event, headers=headers)
        self._send_agent_edited(member.agent)

    def user_associated(self, queue, member):
        event = QueueMemberUserAssociatedEvent(queue.id, member.user.id)
        headers = self._build_headers(tenant_uuid=str(queue.tenant_uuid))
        self.bus.send_bus_event(event, headers=headers)
        self.send_sysconfd_handlers(
            ipbx_command=[
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ]
        )

    def user_dissociated(self, queue, member):
        event = QueueMemberUserDissociatedEvent(queue.id, member.user.id)
        headers = self._build_headers(tenant_uuid=str(queue.tenant_uuid))
        self.bus.send_bus_event(event, headers=headers)
        self.send_sysconfd_handlers(
            ipbx_command=[
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ]
        )


def build_notifier():
    return QueueMemberNotifier(bus, sysconfd)
