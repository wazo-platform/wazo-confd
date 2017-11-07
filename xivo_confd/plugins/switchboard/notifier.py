# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus

from xivo_bus.resources.common.event import ArbitraryEvent
from .schema import SwitchboardSchema


class SwitchboardNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def created(self, switchboard):
        event = ArbitraryEvent(name='switchboard_created',
                               body=SwitchboardSchema().dump(switchboard).data,
                               required_acl='switchboards.{uuid}.created'.format(uuid=switchboard.uuid))
        routing_key = 'config.switchboards.{uuid}.created'.format(uuid=switchboard.uuid)
        self.bus.send_bus_event(event, routing_key)

    def edited(self, switchboard):
        event = ArbitraryEvent(name='switchboard_edited',
                               body=SwitchboardSchema().dump(switchboard).data,
                               required_acl='switchboards.{uuid}.edited'.format(uuid=switchboard.uuid))
        routing_key = 'config.switchboards.{uuid}.edited'.format(uuid=switchboard.uuid)
        self.bus.send_bus_event(event, routing_key)

    def deleted(self, switchboard):
        event = ArbitraryEvent(name='switchboard_deleted',
                               body=SwitchboardSchema().dump(switchboard).data,
                               required_acl='switchboards.{uuid}.deleted'.format(uuid=switchboard.uuid))
        routing_key = 'config.switchboards.{uuid}.deleted'.format(uuid=switchboard.uuid)
        self.bus.send_bus_event(event, routing_key)


def build_notifier():
    return SwitchboardNotifier(bus)
