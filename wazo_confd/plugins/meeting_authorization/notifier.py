# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    CreateMeetingAuthorizationEvent,
    DeleteMeetingAuthorizationEvent,
    EditMeetingAuthorizationEvent,
    UserCreateMeetingAuthorizationEvent,
    UserDeleteMeetingAuthorizationEvent,
    UserEditMeetingAuthorizationEvent,
)

from .schema import MeetingAuthorizationSchema


class Notifier:
    def __init__(self, bus):
        self.bus = bus
        self._schema_instance = MeetingAuthorizationSchema(
            exclude=['guest_sip_authorization']
        )

    def created(self, meeting_authorization):
        meeting_authorization_body = self._schema().dump(meeting_authorization)
        event = CreateMeetingAuthorizationEvent(meeting_authorization_body)
        meeting = meeting_authorization.meeting
        headers = self._build_headers(meeting)
        self.bus.send_bus_event(event, headers)

        for owner_uuid in meeting.owner_uuids:
            event = UserCreateMeetingAuthorizationEvent(
                meeting_authorization_body, owner_uuid
            )
            headers = {
                'name': UserCreateMeetingAuthorizationEvent.name,
                'tenant_uuid': meeting.tenant_uuid,
                f'user:{owner_uuid}': True,
            }
            self.bus.send_bus_event(event, headers)

    def edited(self, meeting_authorization):
        meeting_authorization_body = self._schema().dump(meeting_authorization)
        event = EditMeetingAuthorizationEvent(meeting_authorization_body)
        meeting = meeting_authorization.meeting
        headers = self._build_headers(meeting)
        self.bus.send_bus_event(event, headers)

        for owner_uuid in meeting.owner_uuids:
            event = UserEditMeetingAuthorizationEvent(
                meeting_authorization_body, owner_uuid
            )
            headers = {
                'name': UserEditMeetingAuthorizationEvent.name,
                'tenant_uuid': meeting.tenant_uuid,
                f'user:{owner_uuid}': True,
            }
            self.bus.send_bus_event(event, headers)

    def deleted(self, meeting_authorization):
        meeting_authorization_body = self._schema().dump(meeting_authorization)
        event = DeleteMeetingAuthorizationEvent(meeting_authorization_body)
        meeting = meeting_authorization.meeting
        headers = self._build_headers(meeting)
        self.bus.send_bus_event(event, headers)

        for owner_uuid in meeting.owner_uuids:
            event = UserDeleteMeetingAuthorizationEvent(
                meeting_authorization_body, owner_uuid
            )
            headers = {
                'name': UserDeleteMeetingAuthorizationEvent.name,
                'tenant_uuid': meeting.tenant_uuid,
                f'user:{owner_uuid}': True,
            }
            self.bus.send_bus_event(event, headers)

    def _schema(self):
        return self._schema_instance

    def _build_headers(self, meeting):
        return {'tenant_uuid': str(meeting.tenant_uuid)}
