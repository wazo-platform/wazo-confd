# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.wizard.event import WizardCreatedEvent

from wazo_confd import bus


class WizardNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self):
        event = WizardCreatedEvent()
        self.bus.queue_event(event)


def build_notifier():
    return WizardNotifier(bus)
