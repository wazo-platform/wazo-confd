# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd
from xivo_confd.database import device as device_db

from xivo_bus.resources.func_key.event import (CreateFuncKeyTemplateEvent,
                                               EditFuncKeyTemplateEvent,
                                               DeleteFuncKeyTemplateEvent)


class FuncKeyTemplateNotifier(object):

    def __init__(self, bus, sysconfd, device_db):
        self.bus = bus
        self.sysconfd = sysconfd
        self.device_db = device_db

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, template):
        event = CreateFuncKeyTemplateEvent(template.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, template, updated_fields):
        event = EditFuncKeyTemplateEvent(template.id)
        self.bus.send_bus_event(event, event.routing_key)
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers(['dialplan reload'])
            self._reload_sccp(template)

    def deleted(self, template):
        event = DeleteFuncKeyTemplateEvent(template.id)
        self.bus.send_bus_event(event, event.routing_key)
        self.send_sysconfd_handlers(['dialplan reload'])
        self._reload_sccp(template)

    def _reload_sccp(self, template):
        if self.device_db.template_has_sccp_device(template.id):
            self.send_sysconfd_handlers(['module reload chan_sccp.so'])


def build_notifier():
    return FuncKeyTemplateNotifier(bus, sysconfd, device_db)
