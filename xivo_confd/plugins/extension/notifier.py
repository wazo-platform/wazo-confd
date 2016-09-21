# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_bus.resources.extension.event import CreateExtensionEvent, \
    EditExtensionEvent, DeleteExtensionEvent


class ExtensionNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = CreateExtensionEvent(extension.id,
                                     extension.exten,
                                     extension.context)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, extension, updated_fields):
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers(['dialplan reload',
                                         'sip reload',
                                         'module reload chan_sccp.so',
                                         'module reload app_queue.so'])
        event = EditExtensionEvent(extension.id,
                                   extension.exten,
                                   extension.context)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = DeleteExtensionEvent(extension.id,
                                     extension.exten,
                                     extension.context)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return ExtensionNotifier(sysconfd, bus)
