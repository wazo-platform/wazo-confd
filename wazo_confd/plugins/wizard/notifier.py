# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.wizard.event import CreateWizardEvent

from wazo_confd import bus


class WizardNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self):
        event = CreateWizardEvent()
        self.bus.send_bus_event(event)


def build_notifier():
    return WizardNotifier(bus)
