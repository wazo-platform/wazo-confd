# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.user.event import EditUserFallbackEvent


class UserFallbackNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def edited(self, user):
        event = EditUserFallbackEvent(user.id, user.uuid)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserFallbackNotifier(bus)
