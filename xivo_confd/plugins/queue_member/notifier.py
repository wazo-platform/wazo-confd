# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd
from xivo_bus.resources.queue_members.event import (
    AgentQueueAssociatedEvent,
    AgentQueueAssociationEditedEvent,
    AgentRemovedFromQueueEvent,
)


class QueueMemberNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, cti_command=[], agent_command=[]):
        handlers = {'ctibus': cti_command,
                    'ipbx': [],
                    'agentbus': agent_command}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, queue_member):
        event = AgentQueueAssociatedEvent(queue_member.queue_id,
                                          queue_member.agent_id,
                                          queue_member.penalty)
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(cti_command=['xivo[queuemember,update]'],
                                    agent_command=['agent.edit.{}'.format(queue_member.agent_id)])

    def edited(self, queue_member):
        event = AgentQueueAssociationEditedEvent(queue_member.queue_id,
                                                 queue_member.agent_id,
                                                 queue_member.penalty)
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(agent_command=['agent.edit.{}'.format(queue_member.agent_id)])

    def dissociated(self, queue_member):
        event = AgentRemovedFromQueueEvent(queue_member.queue_id, queue_member.agent_id)
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(cti_command=['xivo[queuemember,update]'],
                                    agent_command=['agent.edit.{}'.format(queue_member.agent_id)])


def build_notifier():
    return QueueMemberNotifier(bus, sysconfd)
