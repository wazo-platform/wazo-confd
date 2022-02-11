# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.func_key.event import (
    CreateFuncKeyTemplateEvent,
    DeleteFuncKeyTemplateEvent,
    EditFuncKeyTemplateEvent,
)

from wazo_confd import bus, sysconfd
from wazo_confd.database import device as device_db_module


class FuncKeyTemplateNotifier:
    def __init__(self, bus, sysconfd, device_db):
        self.bus = bus
        self.sysconfd = sysconfd
        self.device_db = device_db

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ipbx': ipbx, 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, template):
        event = CreateFuncKeyTemplateEvent(template.id)
        headers = self._build_headers(template)
        self.bus.send_bus_event(event, headers=headers)

    def edited(self, template, updated_fields):
        event = EditFuncKeyTemplateEvent(template.id)
        headers = self._build_headers(template)
        self.bus.send_bus_event(event, headers=headers)
        if updated_fields is None or updated_fields:
            self.send_sysconfd_handlers(['dialplan reload'])
            self._reload_sccp(template)

    def deleted(self, template):
        event = DeleteFuncKeyTemplateEvent(template.id)
        headers = self._build_headers(template)
        self.bus.send_bus_event(event, headers=headers)
        self.send_sysconfd_handlers(['dialplan reload'])
        self._reload_sccp(template)

    def _reload_sccp(self, template):
        if self.device_db.template_has_sccp_device(template.id):
            self.send_sysconfd_handlers(['module reload chan_sccp.so'])

    def _build_headers(self, template):
        return {'tenant_uuid': str(template.tenant_uuid)}


def build_notifier():
    return FuncKeyTemplateNotifier(bus, sysconfd, device_db_module)
