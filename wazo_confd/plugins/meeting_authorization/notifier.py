# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    CreateMeetingAuthorizationEvent,
    DeleteMeetingAuthorizationEvent,
    EditMeetingAuthorizationEvent,
    UserCreateMeetingAuthorizationEvent,
)

from .schema import MeetingAuthorizationSchema


class Notifier:
    def __init__(self, bus):
        self.bus = bus
        self._schema_instance = MeetingAuthorizationSchema(
            exclude=['guest_sip_authorization']
        )

    def created(self, meeting_authorization):
        meeting_body = self._schema().dump(meeting_authorization)
        event = CreateMeetingAuthorizationEvent(meeting_body)
        self.bus.send_bus_event(event)
        for owner_uuid in meeting_authorization.meeting.owner_uuids:
            event = UserCreateMeetingAuthorizationEvent(meeting_body, owner_uuid)
            headers = {
                'name': UserCreateMeetingAuthorizationEvent.name,
                f'user:{owner_uuid}': True,
            }
            self.bus.send_bus_event(event, headers)

    def edited(self, meeting_authorization):
        event = EditMeetingAuthorizationEvent(
            self._schema().dump(meeting_authorization)
        )
        self.bus.send_bus_event(event)

    def deleted(self, meeting_authorization):
        event = DeleteMeetingAuthorizationEvent(
            self._schema().dump(meeting_authorization)
        )
        self.bus.send_bus_event(event)

    def _schema(self):
        return self._schema_instance
