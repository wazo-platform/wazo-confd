# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.recordings.event import RecordingsAnnouncementsEditedEvent

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.recordings.schema import RecordingAnnouncementSchema


class RecordingAnnouncementNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': [
                'module reload res_pjsip.so',
            ],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, tenant):
        serialized = RecordingAnnouncementSchema().dump(tenant)
        self.send_sysconfd_handlers()
        event = RecordingsAnnouncementsEditedEvent(serialized, tenant.uuid)
        self.bus.queue_event(event)


def build_notifier():
    return RecordingAnnouncementNotifier(bus, sysconfd)
