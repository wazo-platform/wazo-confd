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

from xivo_confd.helpers.bus_manager import send_bus_event
from xivo_bus.resources.user.event import CreateUserEvent, \
    EditUserEvent, DeleteUserEvent
from xivo_confd.helpers import sysconfd_connector


def _new_sysconfd_data(ctibus_command):
    return {
        'ctibus': [ctibus_command],
        'dird': [],
        'ipbx': ['dialplan reload',
                 'module reload app_queue.so',
                 'sip reload'],
        'agentbus': []
    }


def created(user):
    data = _new_sysconfd_data('xivo[user,add,%s]' % user.id)
    sysconfd_connector.exec_request_handlers(data)
    event = CreateUserEvent(user.id)
    send_bus_event(event, event.routing_key)


def edited(user):
    data = _new_sysconfd_data('xivo[user,edit,%s]' % user.id)
    sysconfd_connector.exec_request_handlers(data)
    event = EditUserEvent(user.id)
    send_bus_event(event, event.routing_key)


def deleted(user):
    data = _new_sysconfd_data('xivo[user,delete,%s]' % user.id)
    sysconfd_connector.exec_request_handlers(data)
    event = DeleteUserEvent(user.id)
    send_bus_event(event, event.routing_key)
