# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.line.event import (
    CreateLineEvent,
    DeleteLineEvent,
    EditLineEvent,
)

from xivo_confd import bus, sysconfd


class LineNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {'ctibus': [],
                    'ipbx': ['module reload res_pjsip.so', 'dialplan reload', 'module reload chan_sccp.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, line):
        self.send_sysconfd_handlers()
        event = CreateLineEvent(line.id)
        self.bus.send_bus_event(event)

    def edited(self, line, updated_fields):
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers()
        event = EditLineEvent(line.id)
        self.bus.send_bus_event(event)

    def deleted(self, line):
        self.send_sysconfd_handlers()
        event = DeleteLineEvent(line.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return LineNotifier(sysconfd, bus)
