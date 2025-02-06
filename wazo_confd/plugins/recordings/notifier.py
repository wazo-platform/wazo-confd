# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.recordings.event import RecordingsAnnouncementsEditedEvent
from wazo_confd.plugins.recordings.schema import RecordingAnnouncementSchema

from wazo_confd import bus


class RecordingAnnouncementNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, tenant):
        serialized = RecordingAnnouncementSchema().dump(tenant)
        event = RecordingsAnnouncementsEditedEvent(serialized, tenant.uuid)
        self.bus.queue_event(event)


def build_notifier():
    return RecordingAnnouncementNotifier(bus)
