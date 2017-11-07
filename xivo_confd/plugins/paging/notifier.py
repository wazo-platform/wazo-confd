# -*- coding: UTF-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.paging.event import (CreatePagingEvent,
                                             EditPagingEvent,
                                             DeletePagingEvent)


class PagingNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, paging):
        event = CreatePagingEvent(paging.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, paging):
        event = EditPagingEvent(paging.id)
        self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, paging):
        event = DeletePagingEvent(paging.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return PagingNotifier(bus)
