# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.entity.event import (
    CreateEntityEvent,
    DeleteEntityEvent,
    EditEntityEvent
)

from xivo_confd import bus


class EntityNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, entity):
        event = CreateEntityEvent(entity.id)
        self.bus.send_bus_event(event)

    def deleted(self, entity):
        event = DeleteEntityEvent(entity.id)
        self.bus.send_bus_event(event)

    def edited(self, entity):
        event = EditEntityEvent(entity.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return EntityNotifier(bus)
