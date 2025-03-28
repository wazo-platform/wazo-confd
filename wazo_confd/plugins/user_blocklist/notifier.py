# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later
from __future__ import annotations
from typing import TypedDict

from wazo_bus.resources.common.types import UUIDStr
from wazo_bus.resources.common.event import UserEvent
from xivo_dao.alchemy.blocklist import BlocklistNumber

from wazo_confd import bus

from .schema import user_blocklist_number_schema


class BlocklistNumberInfo(TypedDict):
    uuid: str
    user_uuid: str
    number: str
    label: str | None
    blocklist_uuid: str


class UserBlocklistNumberCreatedEvent(UserEvent):
    routing_key_fmt = 'confd.users.{user_uuid}.blocklist.created'
    name = 'user_blocklist_number_created'

    def __init__(
        self,
        blocklist_number: BlocklistNumberInfo,
        tenant_uuid: UUIDStr,
        user_uuid: UUIDStr,
    ) -> None:
        super().__init__(blocklist_number, tenant_uuid, user_uuid)


class UserBlocklistNumberEditedEvent(UserEvent):
    routing_key_fmt = 'confd.users.{user_uuid}.blocklist.edited'
    name = 'user_blocklist_number_edited'

    def __init__(
        self,
        blocklist_number: BlocklistNumberInfo,
        tenant_uuid: UUIDStr,
        user_uuid: UUIDStr,
    ) -> None:
        super().__init__(blocklist_number, tenant_uuid, user_uuid)


class UserBlocklistNumberDeletedEvent(UserEvent):
    routing_key_fmt = 'confd.users.{user_uuid}.blocklist.deleted'
    name = 'user_blocklist_number_deleted'

    def __init__(
        self,
        blocklist_number: BlocklistNumberInfo,
        tenant_uuid: UUIDStr,
        user_uuid: UUIDStr,
    ) -> None:
        super().__init__(blocklist_number, tenant_uuid, user_uuid)


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
