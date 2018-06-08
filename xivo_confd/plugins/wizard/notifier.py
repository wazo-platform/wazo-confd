# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.wizard.event import CreateWizardEvent

from xivo_confd import bus


class WizardNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self):
        event = CreateWizardEvent()
        self.bus.send_bus_event(event)


def build_notifier():
    return WizardNotifier(bus)
