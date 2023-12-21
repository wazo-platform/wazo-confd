# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.agent.event import AgentEditedEvent
from xivo_bus.resources.queue_member.event import (
    QueueMemberAgentAssociatedEvent,
    QueueMemberAgentDissociatedEvent,
    QueueMemberUserAssociatedEvent,
    QueueMemberUserDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class QueueMemberNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def _send_agent_edited(self, agent):
        event = AgentEditedEvent(agent.id, agent.tenant_uuid)
        self.bus.queue_event(event)

    def send_sysconfd_handlers(self, ipbx_command=[]):
        handlers = {'ipbx': ipbx_command}
        self.sysconfd.exec_request_handlers(handlers)

    def agent_associated(self, queue, member):
        event = QueueMemberAgentAssociatedEvent(
            queue.id, member.agent.id, member.penalty, queue.tenant_uuid
        )
        self.bus.queue_event(event)
        self._send_agent_edited(member.agent)

    def agent_dissociated(self, queue, member):
        event = QueueMemberAgentDissociatedEvent(
            queue.id, member.agent.id, queue.tenant_uuid
        )
        self.bus.queue_event(event)
        self._send_agent_edited(member.agent)

    def user_associated(self, queue, member):
        event = QueueMemberUserAssociatedEvent(
            queue.id, queue.tenant_uuid, member.user.id
        )
        self.bus.queue_event(event)
        self.send_sysconfd_handlers(
            ipbx_command=[
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ]
        )

    def user_dissociated(self, queue, member):
        event = QueueMemberUserDissociatedEvent(
            queue.id, queue.tenant_uuid, member.user.id
        )
        self.bus.queue_event(event)
        self.send_sysconfd_handlers(
            ipbx_command=[
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ]
        )


def build_notifier():
    return QueueMemberNotifier(bus, sysconfd)
