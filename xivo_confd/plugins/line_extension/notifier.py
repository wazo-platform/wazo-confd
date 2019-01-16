# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.line_extension.event import (
    LineExtensionAssociatedEvent,
    LineExtensionDissociatedEvent,
)
from xivo_dao.resources.user_line import dao as user_line_dao

from xivo_confd import bus, sysconfd


class LineExtensionNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, line, extension):
        handlers = {'ctibus': self._generate_ctibus_commands(line, extension),
                    'ipbx': ['dialplan reload', 'module reload res_pjsip.so', 'module reload app_queue.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line, extension):
        self.send_sysconfd_handlers(line, extension)
        event = LineExtensionAssociatedEvent(line.id, extension.id)
        self.bus.send_bus_event(event)

    def dissociated(self, line, extension):
        self.send_sysconfd_handlers(line, extension)
        event = LineExtensionDissociatedEvent(line.id, extension.id)
        self.bus.send_bus_event(event)

    def _generate_ctibus_commands(self, line, extension):
        commands = ['xivo[phone,edit,%d]' % line.id]

        user_lines = user_line_dao.find_all_by_line_id(line.id)
        for user_line in user_lines:
            if user_line.user_id:
                commands.append('xivo[user,edit,%d]' % user_line.user_id)

        return commands


def build_notifier():
    return LineExtensionNotifier(bus, sysconfd)
