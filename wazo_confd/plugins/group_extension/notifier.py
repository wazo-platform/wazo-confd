# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group_extension.event import (
    GroupExtensionAssociatedEvent,
    GroupExtensionDissociatedEvent,
)

from wazo_confd import bus, sysconfd


class GroupExtensionNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload']}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, group, extension):
        self.send_sysconfd_handlers()
        event = GroupExtensionAssociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            extension_id=extension.id,
        )
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def dissociated(self, group, extension):
        self.send_sysconfd_handlers()
        event = GroupExtensionDissociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            extension_id=extension.id,
        )
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, group):
        return {'tenant_uuid': str(group.tenant_uuid)}


def build_notifier():
    return GroupExtensionNotifier(bus, sysconfd)
