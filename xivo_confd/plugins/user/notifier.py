# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from xivo_bus.resources.user.event import CreateUserEvent, \
    EditUserEvent, DeleteUserEvent


class UserNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, action, user_id):
        cti_command = 'xivo[user,{},{}]'.format(action, user_id)
        handlers = {'ctibus': [cti_command],
                    'dird': [],
                    'ipbx': ['dialplan reload',
                             'module reload app_queue.so',
                             'sip reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, user):
        self.send_sysconfd_handlers('add', user.id)
        event = CreateUserEvent(user.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, user):
        self.send_sysconfd_handlers('edit', user.id)
        event = EditUserEvent(user.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, user):
        self.send_sysconfd_handlers('delete', user.id)
        event = DeleteUserEvent(user.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserNotifier(sysconfd, bus)
