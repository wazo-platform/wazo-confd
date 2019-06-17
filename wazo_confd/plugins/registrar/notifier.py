# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.registrar.event import (
    CreateRegistrarEvent,
    EditRegistrarEvent,
    DeleteRegistrarEvent,
)


class RegistrarNotifier:

    def __init__(self, bus):
        self.bus = bus

    def created(self, registrar):
        event = CreateRegistrarEvent(registrar.registrar)
        self.bus.send_bus_event(event)

    def edited(self, registrar):
        event = EditRegistrarEvent(registrar.registrar)
        self.bus.send_bus_event(event)

    def deleted(self, registrar):
        event = DeleteRegistrarEvent(registrar.registrar)
        self.bus.send_bus_event(event)
