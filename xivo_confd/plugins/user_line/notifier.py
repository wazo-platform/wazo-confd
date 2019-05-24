# -*- coding: utf-8 -*-
# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_line.event import (
    UserLineAssociatedEvent,
    UserLineDissociatedEvent,
)

from xivo_confd import bus, sysconfd
from xivo_confd.plugins.line.schema import LineSchema
from xivo_confd.plugins.user.schema import UserSchema

USER_FIELDS = [
    'id',
    'uuid',
    'tenant_uuid',
]

LINE_FIELDS = [
    'id',
    'name',
    'endpoint_sip.id',
    'endpoint_sccp.id',
    'endpoint_custom.id',
]


class UserLineNotifier:

    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def _send_sysconfd_handlers(self):
        handlers = {
            'ipbx': ['dialplan reload', 'module reload res_pjsip.so'],
            'agentbus': [],
        }
        self._sysconfd.exec_request_handlers(handlers)

    def associated(self, user_line):
        self._send_sysconfd_handlers()
        user_serialized = UserSchema(only=USER_FIELDS).dump(user_line.user).data
        line_serialized = LineSchema(only=LINE_FIELDS).dump(user_line.line).data
        event = UserLineAssociatedEvent(
            user=user_serialized,
            line=line_serialized,
            main_user=user_line.main_user,
            main_line=user_line.main_line,
        )
        self._bus.send_bus_event(event)

    def dissociated(self, user_line):
        self._send_sysconfd_handlers()
        user_serialized = UserSchema(only=USER_FIELDS).dump(user_line.user).data
        line_serialized = LineSchema(only=LINE_FIELDS).dump(user_line.line).data
        event = UserLineDissociatedEvent(
            user=user_serialized,
            line=line_serialized,
            main_user=user_line.main_user,
            main_line=user_line.main_line,
        )
        self._bus.send_bus_event(event)


def build_notifier():
    return UserLineNotifier(bus, sysconfd)
