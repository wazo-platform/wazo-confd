# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.meeting.event import (
    CreateMeetingEvent,
    DeleteMeetingEvent,
    EditMeetingEvent,
)

from wazo_confd import bus, sysconfd

from .schema import MeetingSchema


MEETING_FIELDS = [
    'uuid',
    'name',
    'owner_uuids',
    'ingress_http_uri',
    'guest_sip_authorization',
]


class Notifier:
    def __init__(self, bus, hostname, port, sysconfd):
        self.bus = bus
        self._schema = MeetingSchema(only=MEETING_FIELDS)
        self._schema.context = {'hostname': hostname, 'port': port}
        self.sysconfd = sysconfd

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
        event = CreateMeetingEvent(self._schema.dump(meeting))
        self.bus.send_bus_event(event)

    def edited(self, meeting):
        self.send_sysconfd_handlers()
        event = EditMeetingEvent(self._schema.dump(meeting))
        self.bus.send_bus_event(event)

    def deleted(self, meeting):
        self.send_sysconfd_handlers()
        event = DeleteMeetingEvent(self._schema.dump(meeting))
        self.bus.send_bus_event(event)


def build_notifier(hostname, port):
    return Notifier(bus, hostname, port, sysconfd)
