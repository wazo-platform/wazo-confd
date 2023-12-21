# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group_member.event import (
    GroupMemberExtensionsAssociatedEvent,
    GroupMemberUsersAssociatedEvent,
)

from wazo_confd import bus, sysconfd


class GroupMemberNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': [
                'module reload res_pjsip.so',
                'module reload app_queue.so',
                'module reload chan_sccp.so',
            ]
        }
        self.sysconfd.exec_request_handlers(handlers)

    def users_associated(self, group, members):
        self.send_sysconfd_handlers()
        user_uuids = [member.user.uuid for member in members]
        event = GroupMemberUsersAssociatedEvent(
            group.id, group.uuid, user_uuids, group.tenant_uuid
        )
        self.bus.queue_event(event)

    def extensions_associated(self, group, members):
        self.send_sysconfd_handlers()
        extensions = [
            {'exten': member.extension.exten, 'context': member.extension.context}
            for member in members
        ]
        event = GroupMemberExtensionsAssociatedEvent(
            group.id, group.uuid, extensions, group.tenant_uuid
        )
        self.bus.queue_event(event)


def build_notifier():
    return GroupMemberNotifier(bus, sysconfd)
