# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.sound.event import (
    CreateSoundEvent,
    DeleteSoundEvent,
)

from xivo_confd import bus


class SoundNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, sound):
        event = CreateSoundEvent(sound.name)
        self.bus.send_bus_event(event)

    def deleted(self, sound):
        event = DeleteSoundEvent(sound.name)
        self.bus.send_bus_event(event)


def build_notifier():
    return SoundNotifier(bus)
