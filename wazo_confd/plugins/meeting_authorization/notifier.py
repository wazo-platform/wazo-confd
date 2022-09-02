# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    MeetingAuthorizationCreatedEvent,
    MeetingAuthorizationDeletedEvent,
    MeetingAuthorizationEditedEvent,
    MeetingUserAuthorizationCreatedEvent,
    MeetingUserAuthorizationDeletedEvent,
    MeetingUserAuthorizationEditedEvent,
)

from .schema import MeetingAuthorizationSchema


class Notifier:
    def __init__(self, bus):
        self.bus = bus
        self._schema_instance = MeetingAuthorizationSchema(
            exclude=['guest_sip_authorization']
        )

    def created(self, meeting_authorization):
        meeting = meeting_authorization.meeting
        payload = self._schema().dump(meeting_authorization)
        event = MeetingAuthorizationCreatedEvent(
            payload, meeting.uuid, meeting.tenant_uuid
        )
        self.bus.publish(event)

        for owner_uuid in meeting.owner_uuids:
            event = MeetingUserAuthorizationCreatedEvent(
                payload, meeting.uuid, meeting.tenant_uuid, owner_uuid
            )
            self.bus.publish(event)

    def edited(self, meeting_authorization):
        meeting = meeting_authorization.meeting
        payload = self._schema().dump(meeting_authorization)
        event = MeetingAuthorizationEditedEvent(
            payload, meeting.uuid, meeting.tenant_uuid
        )
        self.bus.publish(event)

        for owner_uuid in meeting.owner_uuids:
            event = MeetingUserAuthorizationEditedEvent(
                payload, meeting.uuid, meeting.tenant_uuid, owner_uuid
            )
            self.bus.publish(event)

    def deleted(self, meeting_authorization):
        meeting = meeting_authorization.meeting
        payload = self._schema().dump(meeting_authorization)
        event = MeetingAuthorizationDeletedEvent(
            payload, meeting.uuid, meeting.tenant_uuid
        )
        self.bus.publish(event)

        for owner_uuid in meeting.owner_uuids:
            event = MeetingUserAuthorizationDeletedEvent(
                payload, meeting.uuid, meeting.tenant_uuid, owner_uuid
            )
            self.bus.publish(event)

    def _schema(self):
        return self._schema_instance
