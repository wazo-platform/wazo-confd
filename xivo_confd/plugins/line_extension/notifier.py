# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from xivo_confd import bus, sysconfd
from xivo_bus.resources.line_extension.event import (LineExtensionAssociatedEvent,
                                                     LineExtensionDissociatedEvent)
from xivo_dao.resources.user_line import dao as user_line_dao


class LineExtensionNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, line_extension):
        handlers = {'ctibus': self._generate_ctibus_commands(line_extension),
                    'ipbx': ['dialplan reload', 'sip reload', 'module reload app_queue.so'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, line_extension):
        self.send_sysconfd_handlers(line_extension)
        event = LineExtensionAssociatedEvent(line_extension.line_id,
                                             line_extension.extension_id)
        self.bus.send_bus_event(event, event.routing_key)

    def dissociated(self, line_extension):
        self.send_sysconfd_handlers(line_extension)
        event = LineExtensionDissociatedEvent(line_extension.line_id,
                                              line_extension.extension_id)
        self.bus.send_bus_event(event, event.routing_key)

    def _generate_ctibus_commands(self, line_extension):
        commands = ['xivo[phone,edit,%d]' % line_extension.line_id]

        user_lines = user_line_dao.find_all_by_line_id(line_extension.line_id)
        for user_line in user_lines:
            if user_line.user_id:
                commands.append('xivo[user,edit,%d]' % user_line.user_id)

        return commands


def build_notifier():
    return LineExtensionNotifier(bus, sysconfd)
