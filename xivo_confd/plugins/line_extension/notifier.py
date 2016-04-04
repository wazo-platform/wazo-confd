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

from xivo_bus.resources.line_extension import event

from xivo_dao.resources.user_line import dao as user_line_dao

from xivo_confd.helpers import bus_manager
from xivo_confd.helpers import sysconfd_connector


def associated(line_extension):
    send_sysconf_commands(line_extension)
    send_bus_association_events(line_extension)


def send_sysconf_commands(line_extension):
    command = {
        'ctibus': _generate_ctibus_commands(line_extension),
        'ipbx': ['dialplan reload', 'sip reload'],
        'agentbus': [],
    }

    sysconfd_connector.exec_request_handlers(command)


def _generate_ctibus_commands(line_extension):
    commands = ['xivo[phone,edit,%d]' % line_extension.line_id]

    user_lines = user_line_dao.find_all_by_line_id(line_extension.line_id)
    for user_line in user_lines:
        if user_line.user_id:
            commands.append('xivo[user,edit,%d]' % user_line.user_id)

    return commands


def send_bus_association_events(line_extension):
    bus_event = event.LineExtensionAssociatedEvent(line_extension.line_id,
                                                   line_extension.extension_id)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)


def dissociated(line_extension):
    send_sysconf_commands(line_extension)
    send_bus_dissociation_events(line_extension)


def send_bus_dissociation_events(line_extension):
    bus_event = event.LineExtensionDissociatedEvent(line_extension.line_id,
                                                    line_extension.extension_id)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
