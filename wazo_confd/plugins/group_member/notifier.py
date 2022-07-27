# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group_member.event import (
    GroupMemberUsersAssociatedEvent,
    GroupMemberExtensionsAssociatedEvent,
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
            group_id=group.id,
            group_uuid=str(group.uuid),
            user_uuids=user_uuids,
        )
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def extensions_associated(self, group, members):
        self.send_sysconfd_handlers()
        extensions = [
            {'exten': member.extension.exten, 'context': member.extension.context}
            for member in members
        ]
        event = GroupMemberExtensionsAssociatedEvent(
            group_id=group.id,
            group_uuid=str(group.uuid),
            extensions=extensions,
        )
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, group):
        return {'tenant_uuid': str(group.tenant_uuid)}


def build_notifier():
    return GroupMemberNotifier(bus, sysconfd)
