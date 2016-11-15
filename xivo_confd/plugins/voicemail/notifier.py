# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_bus.resources.voicemail.event import (CreateVoicemailEvent,
                                                EditVoicemailEvent,
                                                EditUserVoicemailEvent,
                                                DeleteVoicemailEvent)
from xivo_dao.resources.user_voicemail import dao as user_voicemail_dao


class VoicemailNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def _send_sysconfd_handlers(self, ctibus_command, ipbx_commands):
        handlers = {
            'ctibus': [ctibus_command],
            'ipbx': ipbx_commands,
            'agentbus': []
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,add,%s]' % voicemail.id,
                                     ['voicemail reload'])
        event = CreateVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,edit,%s]' % voicemail.id,
                                     ['voicemail reload',
                                      'sip reload',
                                      'module reload chan_sccp.so'])
        event = EditVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event, event.routing_key)
        for user_voicemail in user_voicemail_dao.find_all_by_voicemail_id(voicemail.id):
            event = EditUserVoicemailEvent(user_voicemail.user_uuid, voicemail.id)
            self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,delete,%s]' % voicemail.id,
                                     ['voicemail reload'])
        event = DeleteVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return VoicemailNotifier(bus, sysconfd)
