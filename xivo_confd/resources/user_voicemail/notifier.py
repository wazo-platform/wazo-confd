# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.helpers import sysconfd_connector
from xivo_dao.helpers import bus_manager


def associated(user_voicemail):
    sysconf_command_association_updated(user_voicemail)
    bus_event_associated(user_voicemail)


def dissociated(user_voicemail):
    sysconf_command_association_updated(user_voicemail)
    bus_event_dissociated(user_voicemail)


def sysconf_command_association_updated(user_voicemail):
    command = {
        'dird': [],
        'ipbx': ['sip reload'],
        'agentbus': [],
        'ctibus': _generate_ctibus_commands(user_voicemail)
    }
    sysconfd_connector.exec_request_handlers(command)


def _generate_ctibus_commands(user_voicemail):
    ctibus = ['xivo[user,edit,%d]' % user_voicemail.user_id]

    user_lines = user_line_dao.find_all_by_user_id(user_voicemail.user_id)
    for user_line in user_lines:
        ctibus.append('xivo[phone,edit,%d]' % user_line.line_id)

    return ctibus


def bus_event_associated(user_voicemail):
    bus_event = event.UserVoicemailAssociatedEvent(user_voicemail.user_id,
                                                   user_voicemail.voicemail_id,
                                                   user_voicemail.enabled)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)


def bus_event_dissociated(user_voicemail):
    bus_event = event.UserVoicemailDissociatedEvent(user_voicemail.user_id,
                                                    user_voicemail.voicemail_id,
                                                    False)
    bus_manager.send_bus_event(bus_event, bus_event.routing_key)
