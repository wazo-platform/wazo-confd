# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.group.event import EditGroupFallbackEvent


class GroupFallbackNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def edited(self, group):
        event = EditGroupFallbackEvent(group.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return GroupFallbackNotifier(bus)
