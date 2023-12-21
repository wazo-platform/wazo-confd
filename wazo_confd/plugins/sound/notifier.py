# Copyright 2017-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.sound.event import SoundCreatedEvent, SoundDeletedEvent

from wazo_confd import bus


class SoundNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, sound):
        event = SoundCreatedEvent(sound.name, sound.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, sound):
        event = SoundDeletedEvent(sound.name, sound.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return SoundNotifier(bus)
