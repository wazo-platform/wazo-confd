# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

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

    def send_sysconfd_handlers(self, ipbx_command=[], agent_command=[]):
        handlers = {
            'ipbx': ipbx_command,
            'agentbus': agent_command,
        }
        self.sysconfd.exec_request_handlers(handlers)

    def agent_associated(self, queue, member):
        event = QueueMemberAgentAssociatedEvent(
            queue.id,
            member.agent.id,
            member.penalty,
        )
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(
            # Only used if the agent is logged
            # EditAgentEvent can be sent without passing by sysconfd
            agent_command=['agent.edit.{}'.format(member.agent.id)]
        )

    def agent_dissociated(self, queue, member):
        event = QueueMemberAgentDissociatedEvent(queue.id, member.agent.id)
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(
            # Only used if the agent is logged
            # EditAgentEvent can be sent without passing by sysconfd
            agent_command=['agent.edit.{}'.format(member.agent.id)],
        )

    def user_associated(self, queue, member):
        event = QueueMemberUserAssociatedEvent(queue.id, member.user.id)
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(
            ipbx_command=['module reload res_pjsip.so', 'module reload app_queue.so', 'module reload chan_sccp.so'],
        )

    def user_dissociated(self, queue, member):
        event = QueueMemberUserDissociatedEvent(queue.id, member.user.id)
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(
            ipbx_command=['module reload res_pjsip.so', 'module reload app_queue.so', 'module reload chan_sccp.so'],
        )


def build_notifier():
    return QueueMemberNotifier(bus, sysconfd)
