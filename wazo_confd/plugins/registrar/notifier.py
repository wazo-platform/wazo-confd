# Copyright 2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.registrar.event import (
    CreateRegistrarEvent,
    EditRegistrarEvent,
    DeleteRegistrarEvent,
)
from .schema import RegistrarSchema


class RegistrarNotifier:

    schema = RegistrarSchema(exclude=['links'])

    def __init__(self, bus):
        self.bus = bus

    def created(self, registrar):
        event = CreateRegistrarEvent(self.schema.dump(registrar))
        self.bus.send_bus_event(event)

    def edited(self, registrar):
        event = EditRegistrarEvent(self.schema.dump(registrar))
        self.bus.send_bus_event(event)

    def deleted(self, registrar):
        event = DeleteRegistrarEvent(self.schema.dump(registrar))
        self.bus.send_bus_event(event)
