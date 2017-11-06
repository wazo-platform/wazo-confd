# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from xivo_confd import bus, sysconfd

from xivo_bus.resources.voicemail_zonemessages.event import EditVoicemailZoneMessagesEvent


class VoicemailZoneMessagesNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, voicemail_zonemessages):
        event = EditVoicemailZoneMessagesEvent()
        self.bus.send_bus_event(event, event.routing_key)
        self.send_sysconfd_handlers(['voicemail reload'])


def build_notifier():
    return VoicemailZoneMessagesNotifier(bus, sysconfd)
