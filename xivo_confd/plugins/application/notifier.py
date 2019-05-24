# -*- coding: utf-8 -*-
# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.application.event import (
    CreateApplicationEvent,
    DeleteApplicationEvent,
    EditApplicationEvent,
)

from xivo_confd import bus


class ApplicationNotifier:

    def __init__(self, bus):
        self.bus = bus

    def created(self, application):
        event = CreateApplicationEvent(application.uuid)
        self.bus.send_bus_event(event)

    def edited(self, application):
        event = EditApplicationEvent(application.uuid)
        self.bus.send_bus_event(event)

    def deleted(self, application):
        event = DeleteApplicationEvent(application.uuid)
        self.bus.send_bus_event(event)


def build_notifier():
    return ApplicationNotifier(bus)
