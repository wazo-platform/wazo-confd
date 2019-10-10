# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.queue_general.event import EditQueueGeneralEvent

from wazo_confd import bus, sysconfd


class QueueGeneralNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, queue_general):
        event = EditQueueGeneralEvent()
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['module reload app_queue.so'])


def build_notifier():
    return QueueGeneralNotifier(bus, sysconfd)
