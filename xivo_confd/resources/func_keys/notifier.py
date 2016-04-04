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

from xivo_bus.resources.func_key.event import CreateFuncKeyTemplateEvent, \
    EditFuncKeyTemplateEvent, DeleteFuncKeyTemplateEvent


class FuncKeyTemplateNotifier(object):

    REQUEST_HANDLERS = {'ipbx': ['module reload chan_sccp.so'],
                        'agentbus': [],
                        'ctibus': []}

    def __init__(self, bus, sysconfd, device_db):
        self.bus = bus
        self.sysconfd = sysconfd
        self.device_db = device_db

    def created(self, template):
        event = CreateFuncKeyTemplateEvent(template.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, template):
        event = EditFuncKeyTemplateEvent(template.id)
        self.bus.send_bus_event(event, event.routing_key)
        self.reload_sccp(template)

    def deleted(self, template):
        event = DeleteFuncKeyTemplateEvent(template.id)
        self.bus.send_bus_event(event, event.routing_key)
        self.reload_sccp(template)

    def reload_sccp(self, template):
        if self.device_db.template_has_sccp_device(template.id):
            self.sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)
