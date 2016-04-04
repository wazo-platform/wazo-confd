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

from xivo_confd.helpers.bus_manager import send_bus_event
from xivo_confd.helpers import sysconfd_connector

from xivo_bus.resources.voicemail.event import CreateVoicemailEvent
from xivo_bus.resources.voicemail.event import EditVoicemailEvent
from xivo_bus.resources.voicemail.event import DeleteVoicemailEvent


def _new_sysconfd_data(ctibus_command, ipbx_commands):
    return {
        'ctibus': [ctibus_command],
        'ipbx': ipbx_commands,
        'agentbus': []
    }


def created(voicemail):
    data = _new_sysconfd_data('xivo[voicemail,add,%s]' % voicemail.id,
                              ['voicemail reload'])
    sysconfd_connector.exec_request_handlers(data)
    event = CreateVoicemailEvent(voicemail.id)
    send_bus_event(event, event.routing_key)


def edited(voicemail):
    data = _new_sysconfd_data('xivo[voicemail,edit,%s]' % voicemail.id,
                              ['voicemail reload',
                               'sip reload',
                               'module reload chan_sccp.so'])
    sysconfd_connector.exec_request_handlers(data)
    event = EditVoicemailEvent(voicemail.id)
    send_bus_event(event, event.routing_key)


def deleted(voicemail):
    data = _new_sysconfd_data('xivo[voicemail,delete,%s]' % voicemail.id,
                              ['voicemail reload'])
    sysconfd_connector.exec_request_handlers(data)
    event = DeleteVoicemailEvent(voicemail.id)
    send_bus_event(event, event.routing_key)
