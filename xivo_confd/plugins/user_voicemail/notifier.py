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

from xivo_bus.resources.user_voicemail import event
from xivo_confd.helpers import sysconfd_connector
from xivo_confd.helpers import bus_manager


def associated(user, voicemail):
    sysconf_command_association_updated(user)
    bus_event_associated(user, voicemail)


def dissociated(user, voicemail):
    sysconf_command_association_updated(user)
    bus_event_dissociated(user, voicemail)


def sysconf_command_association_updated(user):
    command = {
        'ipbx': ['sip reload', 'module reload chan_sccp.so'],
        'agentbus': [],
        'ctibus': _generate_ctibus_commands(user)
    }
    sysconfd_connector.exec_request_handlers(command)


def _generate_ctibus_commands(user):
    ctibus = ['xivo[user,edit,%d]' % user.id]

    for line in user.lines:
        ctibus.append('xivo[phone,edit,%d]' % line.id)

    return ctibus


def bus_event_associated(user, voicemail):
    bus_event = event.UserVoicemailAssociatedEvent(user.uuid, voicemail.id)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)


def bus_event_dissociated(user, voicemail):
    bus_event = event.UserVoicemailDissociatedEvent(user.uuid, voicemail.id)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
