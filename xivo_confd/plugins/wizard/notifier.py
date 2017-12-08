# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.wizard.event import CreateWizardEvent


class WizardNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self):
        event = CreateWizardEvent()
        self.bus.send_bus_event(event)


def build_notifier():
    return WizardNotifier(bus)
