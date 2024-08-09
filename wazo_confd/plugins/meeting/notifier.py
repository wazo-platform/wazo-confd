# Copyright 2021-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo.xivo_helpers import clean_extension
from wazo_bus.resources.meeting.event import (
    MeetingCreatedEvent,
    MeetingDeletedEvent,
    MeetingEditedEvent,
    MeetingProgressEvent,
    MeetingUserProgressEvent,
)

from wazo_confd import auth

from .schema import MeetingSchema


MEETING_FIELDS = [
    'uuid',
    'name',
    'owner_uuids',
    'ingress_http_uri',
    'guest_sip_authorization',
]


class Notifier:
    def __init__(
        self,
        bus,
        sysconfd,
        ingress_http_service,
        extension_features_service,
        preset_tenant_uuid=None,
        immediate=False,
    ):
        self.bus = bus
        self.immediate = immediate
        self._schema_instance = MeetingSchema(only=MEETING_FIELDS)
        self.sysconfd = sysconfd
        self._ingress_http_service = ingress_http_service
        self._extension_features_service = extension_features_service
        self._preset_tenant_uuid = preset_tenant_uuid

    @property
    def send_bus_event(self):
        return self.bus.publish if self.immediate else self.bus.queue_event

    def send_sysconfd_handlers(self, meeting, action):
        handlers = {
            'ipbx': ['module reload res_pjsip.so'],
            'context': [
                {
                    'resource_type': 'meeting',
                    'resource_action': action,
                    'resource_body': {'uuid': str(meeting.uuid)},
                }
            ],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, meeting):
        self.send_sysconfd_handlers(meeting, 'created')
        payload = self._schema().dump(meeting)
        event = MeetingCreatedEvent(payload, meeting.tenant_uuid)
        self.send_bus_event(event)

    def edited(self, meeting):
        self.send_sysconfd_handlers(meeting, 'edited')
        payload = self._schema().dump(meeting)
        event = MeetingEditedEvent(payload, meeting.tenant_uuid)
        self.send_bus_event(event)

    def deleted(self, meeting):
        self.send_sysconfd_handlers(meeting, 'deleted')
        payload = self._schema().dump(meeting)
        event = MeetingDeletedEvent(payload, meeting.tenant_uuid)
        self.send_bus_event(event)

    def ready(self, meeting):
        meeting_body = self._schema().dump(meeting)
        event = MeetingProgressEvent(meeting_body, 'ready', meeting.tenant_uuid)
        self.send_bus_event(event)

        for owner_uuid in meeting_body['owner_uuids']:
            event = MeetingUserProgressEvent(
                meeting_body, 'ready', meeting.tenant_uuid, owner_uuid
            )
            self.send_bus_event(event)

    def _schema(self):
        if self._preset_tenant_uuid:
            tenant_uuid = self._preset_tenant_uuid
        else:
            tenant_uuid = str(auth.master_tenant_uuid)

        ingress_http = self._ingress_http_service.find_by(tenant_uuid=tenant_uuid)
        exten_pattern = None
        exten_prefix = None
        extens = self._extension_features_service.search(
            {'feature': 'meetingjoin'}
        ).items
        for exten in extens:
            if exten.feature == 'meetingjoin' and exten.enabled:
                exten_pattern = exten.exten
                break
        if exten_pattern:
            exten_prefix = clean_extension(exten_pattern)
        self._schema_instance.context = {
            'default_ingress_http': ingress_http,
            'exten_prefix': exten_prefix,
        }
        return self._schema_instance
