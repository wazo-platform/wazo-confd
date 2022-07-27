# Copyright 2019-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.application.schema import ApplicationSchema
from wazo_confd.plugins.line.schema import LineSchema

from xivo_bus.resources.line_application.event import (
    LineApplicationAssociatedEvent,
    LineApplicationDissociatedEvent,
)

LINE_FIELDS = [
    'id',
    'name',
    'endpoint_sip.uuid',
    'endpoint_sccp.id',
    'endpoint_custom.id',
]

APPLICATION_FIELDS = ['uuid']


class LineApplicationNotifier:

    REQUEST_HANDLERS = {'ipbx': ['module reload res_pjsip.so']}

    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def associated(self, line, application):
        self._sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)

        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        application_serialized = ApplicationSchema(only=APPLICATION_FIELDS).dump(
            application
        )
        event = LineApplicationAssociatedEvent(
            line=line_serialized, application=application_serialized
        )
        headers = self._build_headers(line)
        self._bus.send_bus_event(event, headers=headers)

    def dissociated(self, line, application):
        self._sysconfd.exec_request_handlers(self.REQUEST_HANDLERS)

        line_serialized = LineSchema(only=LINE_FIELDS).dump(line)
        application_serialized = ApplicationSchema(only=APPLICATION_FIELDS).dump(
            application
        )
        event = LineApplicationDissociatedEvent(
            line=line_serialized, application=application_serialized
        )
        headers = self._build_headers(line)
        self._bus.send_bus_event(event, headers=headers)

    def _build_headers(self, line):
        return {'tenant_uuid': str(line.tenant_uuid)}


def build_notifier():
    return LineApplicationNotifier(bus, sysconfd)
