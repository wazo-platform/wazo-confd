# Copyright 2016-2021 The Wazo Authors  (see the AUTHORS file)
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
        handlers = {'ipbx': ['dialplan reload'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, group, extension):
        self.send_sysconfd_handlers()
        event = GroupExtensionAssociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            extension_id=extension.id,
        )
        self.bus.send_bus_event(event)

    def dissociated(self, group, extension):
        self.send_sysconfd_handlers()
        event = GroupExtensionDissociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            extension_id=extension.id,
        )
        self.bus.send_bus_event(event)


def build_notifier():
    return GroupExtensionNotifier(bus, sysconfd)
