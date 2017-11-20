# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.wizard.event import CreateWizardEvent


class WizardNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self):
        event = CreateWizardEvent()
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return WizardNotifier(bus)
