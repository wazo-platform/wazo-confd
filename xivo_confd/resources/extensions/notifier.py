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
from xivo_bus.resources.extension.event import CreateExtensionEvent, \
    EditExtensionEvent, DeleteExtensionEvent
from xivo_confd.helpers import sysconfd_connector


def build_request(ipbx):
    return {'ctibus': [],
            'ipbx': ipbx,
            'agentbus': []}


def created(extension):
    request = build_request(['dialplan reload'])
    sysconfd_connector.exec_request_handlers(request)
    event = CreateExtensionEvent(extension.id,
                                 extension.exten,
                                 extension.context)
    send_bus_event(event, event.routing_key)


def edited(extension):
    request = build_request(['dialplan reload', 'sip reload', 'module reload chan_sccp.so'])
    sysconfd_connector.exec_request_handlers(request)
    event = EditExtensionEvent(extension.id,
                               extension.exten,
                               extension.context)
    send_bus_event(event, event.routing_key)


def deleted(extension):
    request = build_request(['dialplan reload'])
    sysconfd_connector.exec_request_handlers(request)
    event = DeleteExtensionEvent(extension.id,
                                 extension.exten,
                                 extension.context)
    send_bus_event(event, event.routing_key)
