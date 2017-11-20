# -*- coding: UTF-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.entity.event import (CreateEntityEvent,
                                             DeleteEntityEvent,
                                             EditEntityEvent)


class EntityNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, entity):
        event = CreateEntityEvent(entity.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, entity):
        event = DeleteEntityEvent(entity.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, entity):
        event = EditEntityEvent(entity.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return EntityNotifier(bus)
