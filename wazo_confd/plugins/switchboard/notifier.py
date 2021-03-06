# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.common.event import ArbitraryEvent

from wazo_confd import bus

from .schema import SwitchboardSchema


class SwitchboardNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, switchboard):
        event = ArbitraryEvent(
            name='switchboard_created',
            body=SwitchboardSchema().dump(switchboard),
            required_acl='switchboards.{uuid}.created'.format(uuid=switchboard.uuid),
        )
        event.routing_key = 'config.switchboards.{uuid}.created'.format(
            uuid=switchboard.uuid
        )
        self.bus.send_bus_event(event)

    def edited(self, switchboard):
        event = ArbitraryEvent(
            name='switchboard_edited',
            body=SwitchboardSchema().dump(switchboard),
            required_acl='switchboards.{uuid}.edited'.format(uuid=switchboard.uuid),
        )
        event.routing_key = 'config.switchboards.{uuid}.edited'.format(
            uuid=switchboard.uuid
        )
        self.bus.send_bus_event(event)

    def deleted(self, switchboard):
        event = ArbitraryEvent(
            name='switchboard_deleted',
            body=SwitchboardSchema().dump(switchboard),
            required_acl='switchboards.{uuid}.deleted'.format(uuid=switchboard.uuid),
        )
        event.routing_key = 'config.switchboards.{uuid}.deleted'.format(
            uuid=switchboard.uuid
        )
        self.bus.send_bus_event(event)


def build_notifier():
    return SwitchboardNotifier(bus)
