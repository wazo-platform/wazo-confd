# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    CreateMeetingEvent,
    DeleteMeetingEvent,
    EditMeetingEvent,
)

from wazo_confd import bus

from .schema import MeetingSchema


MEETING_FIELDS = [
    'uuid',
    'name',
    'owner_uuids',
    'hostname',
    'port',
    # TODO(pc-m): uncomment once the fields get added to the schema
    # 'guest_sip_authorization',
]


class Notifier:
    def __init__(self, bus, hostname, port):
        self.bus = bus
        self._schema = MeetingSchema(only=MEETING_FIELDS)
        self._schema.context = {'hostname': hostname, 'port': port}

    def created(self, meeting):
        event = CreateMeetingEvent(self._schema.dump(meeting))
        self.bus.send_bus_event(event)

    def edited(self, meeting):
        event = EditMeetingEvent(self._schema.dump(meeting))
        self.bus.send_bus_event(event)

    def deleted(self, meeting):
        event = DeleteMeetingEvent(self._schema.dump(meeting))
        self.bus.send_bus_event(event)


def build_notifier(hostname, port):
    return Notifier(bus, hostname, port)
