# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.sound.event import CreateSoundEvent, DeleteSoundEvent

from wazo_confd import bus


class SoundNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, sound):
        event = CreateSoundEvent(sound.name)
        headers = self._build_headers(sound)
        self.bus.send_bus_event(event, headers=headers)

    def deleted(self, sound):
        event = DeleteSoundEvent(sound.name)
        headers = self._build_headers(sound)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, sound):
        return {'tenant_uuid': str(sound.tenant_uuid)}


def build_notifier():
    return SoundNotifier(bus)
