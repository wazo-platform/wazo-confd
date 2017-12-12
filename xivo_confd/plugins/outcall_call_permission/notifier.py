# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus
from xivo_bus.resources.outcall_call_permission.event import (
    OutcallCallPermissionAssociatedEvent,
    OutcallCallPermissionDissociatedEvent,
)


class OutcallCallPermissionNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def associated(self, outcall, call_permission):
        event = OutcallCallPermissionAssociatedEvent(outcall.id, call_permission.id)
        self.bus.send_bus_event(event)

    def dissociated(self, outcall, call_permission):
        event = OutcallCallPermissionDissociatedEvent(outcall.id, call_permission.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return OutcallCallPermissionNotifier(bus)
