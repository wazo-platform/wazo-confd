# Copyright 2016-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.group.event import (
    CreateGroupEvent,
    EditGroupEvent,
    DeleteGroupEvent,
)

from wazo_confd import bus, sysconfd

from .schema import GroupSchema

GROUP_FIELDS = ['id', 'uuid']


class GroupNotifier:
    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self):
        handlers = {'ipbx': ['module reload app_queue.so'], 'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, group):
        return self._dispatch_event(group, CreateGroupEvent)

    def edited(self, group):
        return self._dispatch_event(group, EditGroupEvent)

    def deleted(self, group):
        return self._dispatch_event(group, DeleteGroupEvent)

    def _dispatch_event(self, group, Event):
        self.send_sysconfd_handlers()
        group_serialized = GroupSchema(only=GROUP_FIELDS).dump(group)
        event = Event(**group_serialized)
        headers = self._build_headers(group)
        self.bus.send_bus_event(event, headers=headers)

    def _build_headers(self, group):
        return {'tenant_uuid': str(group.tenant_uuid)}


def build_notifier():
    return GroupNotifier(bus, sysconfd)
