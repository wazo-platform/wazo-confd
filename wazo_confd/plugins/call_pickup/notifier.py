# Copyright 2018-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.call_pickup.event import (
    CallPickupCreatedEvent,
    CallPickupDeletedEvent,
    CallPickupEditedEvent,
)

from wazo_confd import bus, sysconfd


class CallPickupNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['module reload res_pjsip.so', 'module reload chan_sccp.so']
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, call_pickup):
        event = CallPickupCreatedEvent(call_pickup.id, call_pickup.tenant_uuid)
        self.bus.queue_event(event)

    def edited(self, call_pickup):
        event = CallPickupEditedEvent(call_pickup.id, call_pickup.tenant_uuid)
        self.bus.queue_event(event)

    def deleted(self, call_pickup):
        self.send_sysconfd_handlers()
        event = CallPickupDeletedEvent(call_pickup.id, call_pickup.tenant_uuid)
        self.bus.queue_event(event)


def build_notifier():
    return CallPickupNotifier(bus, sysconfd)
