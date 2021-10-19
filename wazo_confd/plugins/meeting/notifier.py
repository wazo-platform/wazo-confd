# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    CreateMeetingEvent,
    DeleteMeetingEvent,
    EditMeetingEvent,
)

from wazo_confd import auth, bus, sysconfd

from .schema import MeetingSchema


MEETING_FIELDS = [
    'uuid',
    'name',
    'owner_uuids',
    'ingress_http_uri',
    'guest_sip_authorization',
]


class Notifier:
    def __init__(self, bus, sysconfd, ingress_http_service, preset_tenant_uuid=None):
        self.bus = bus
        self._schema_instance = MeetingSchema(only=MEETING_FIELDS)
        self.sysconfd = sysconfd
        self._ingress_http_service = ingress_http_service
        self._preset_tenant_uuid = preset_tenant_uuid

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': [
                'dialplan reload',
                'module reload res_pjsip.so',
            ],
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, meeting):
        self.send_sysconfd_handlers()
        event = CreateMeetingEvent(self._schema().dump(meeting))
        self.bus.send_bus_event(event)

    def edited(self, meeting):
        self.send_sysconfd_handlers()
        event = EditMeetingEvent(self._schema().dump(meeting))
        self.bus.send_bus_event(event)

    def deleted(self, meeting):
        self.send_sysconfd_handlers()
        event = DeleteMeetingEvent(self._schema().dump(meeting))
        self.bus.send_bus_event(event)

    def _schema(self):
        if self._preset_tenant_uuid:
            tenant_uuid = self._preset_tenant_uuid
        else:
            tenant_uuid = str(auth.master_tenant_uuid)

        ingress_http = self._ingress_http_service.find_by(tenant_uuid=tenant_uuid)
        self._schema_instance.context = {'default_ingress_http': ingress_http}
        return self._schema_instance


def build_notifier(ingress_http_service):
    return Notifier(bus, sysconfd, ingress_http_service)
