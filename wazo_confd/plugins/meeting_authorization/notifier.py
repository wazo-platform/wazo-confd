# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    CreateMeetingAuthorizationEvent,
    DeleteMeetingAuthorizationEvent,
    EditMeetingAuthorizationEvent,
)

from .schema import MeetingAuthorizationSchema


class Notifier:
    def __init__(self, bus):
        self.bus = bus
        self._schema_instance = MeetingAuthorizationSchema()

    def created(self, meeting):
        event = CreateMeetingAuthorizationEvent(self._schema().dump(meeting))
        self.bus.send_bus_event(event)

    def edited(self, meeting):
        event = EditMeetingAuthorizationEvent(self._schema().dump(meeting))
        self.bus.send_bus_event(event)

    def deleted(self, meeting):
        event = DeleteMeetingAuthorizationEvent(self._schema().dump(meeting))
        self.bus.send_bus_event(event)

    def _schema(self):
        return self._schema_instance
