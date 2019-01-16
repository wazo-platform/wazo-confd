# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.outcall_trunk.event import OutcallTrunksAssociatedEvent

from xivo_confd import bus


class OutcallTrunkNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated_all_trunks(self, outcall, trunks):
        trunk_ids = [trunk.id for trunk in trunks]
        event = OutcallTrunksAssociatedEvent(outcall.id, trunk_ids)
        self.bus.send_bus_event(event)


def build_notifier():
    return OutcallTrunkNotifier(bus)
