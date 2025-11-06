# Copyright 2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations

from wazo_bus.resources.user_blocklist.event import (
    UserBlocklistNumberCreatedEvent,
    UserBlocklistNumberDeletedEvent,
    UserBlocklistNumberEditedEvent,
)
from xivo_dao.alchemy.blocklist_number import BlocklistNumber

from wazo_confd import bus

from .schema import user_blocklist_number_schema


class UserBlocklistNotifier:
    def __init__(self, bus):
        self.bus = bus

    def created(self, resource: BlocklistNumber):
        blocklist_number_serialized = user_blocklist_number_schema.dump(resource)
        event = UserBlocklistNumberCreatedEvent(
            blocklist_number=blocklist_number_serialized,
            tenant_uuid=resource.blocklist.tenant_uuid,
            user_uuid=resource.user_uuid,
        )
        self.bus.queue_event(event)

    def edited(self, resource: BlocklistNumber):
        blocklist_number_serialized = user_blocklist_number_schema.dump(resource)
        event = UserBlocklistNumberEditedEvent(
            blocklist_number=blocklist_number_serialized,
            tenant_uuid=resource.blocklist.tenant_uuid,
            user_uuid=resource.user_uuid,
        )
        self.bus.queue_event(event)

    def deleted(self, resource: BlocklistNumber):
        blocklist_number_serialized = user_blocklist_number_schema.dump(resource)
        event = UserBlocklistNumberDeletedEvent(
            blocklist_number=blocklist_number_serialized,
            tenant_uuid=resource.blocklist.tenant_uuid,
            user_uuid=resource.user_uuid,
        )
        self.bus.queue_event(event)


def build_notifier():
    return UserBlocklistNotifier(bus)
