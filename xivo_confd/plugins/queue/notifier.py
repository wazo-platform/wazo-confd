# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.queue.event import (
    CreateQueueEvent,
    EditQueueEvent,
    DeleteQueueEvent,
)

from xivo_confd import bus, sysconfd


class QueueNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ctibus_command):
        handlers = {'ctibus': [ctibus_command],
                    'ipbx': ['module reload app_queue.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, queue):
        ctibus_command = 'xivo[queue,add,{queue_id}]'.format(queue_id=queue.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = CreateQueueEvent(queue.id)
        self.bus.send_bus_event(event)

    def edited(self, queue):
        ctibus_command = 'xivo[queue,edit,{queue_id}]'.format(queue_id=queue.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = EditQueueEvent(queue.id)
        self.bus.send_bus_event(event)

    def deleted(self, queue):
        ctibus_command = 'xivo[queue,delete,{queue_id}]'.format(queue_id=queue.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = DeleteQueueEvent(queue.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return QueueNotifier(bus, sysconfd)
