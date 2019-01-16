# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group.event import EditGroupFallbackEvent

from xivo_confd import bus


class GroupFallbackNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def edited(self, group):
        event = EditGroupFallbackEvent(group.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupFallbackNotifier(bus)
