# Copyright 2013-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_bus.resources.user_line.event import (
    UserLineAssociatedEvent,
    UserLineDissociatedEvent,
)

from wazo_confd import bus, sysconfd
from wazo_confd.plugins.line.schema import LineSchema
from wazo_confd.plugins.user.schema import UserSchema

USER_FIELDS = ['id', 'uuid', 'tenant_uuid']

LINE_FIELDS = [
    'id',
    'name',
    'endpoint_sip.uuid',
    'endpoint_sccp.id',
    'endpoint_custom.id',
]


class UserLineNotifier:
    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def _send_sysconfd_handlers(self):
        handlers = {'ipbx': ['dialplan reload', 'module reload res_pjsip.so']}
        self._sysconfd.exec_request_handlers(handlers)

    def associated(self, user_line):
        self._send_sysconfd_handlers()
        user_serialized = UserSchema(only=USER_FIELDS).dump(user_line.user)
        line_serialized = LineSchema(only=LINE_FIELDS).dump(user_line.line)
        event = UserLineAssociatedEvent(
            user_serialized,
            line_serialized,
            user_line.main_user,
            user_line.main_line,
            user_line.user.tenant_uuid,
        )
        self._bus.queue_event(event)

    def dissociated(self, user_line):
        self._send_sysconfd_handlers()
        user_serialized = UserSchema(only=USER_FIELDS).dump(user_line.user)
        line_serialized = LineSchema(only=LINE_FIELDS).dump(user_line.line)
        event = UserLineDissociatedEvent(
            user_serialized,
            line_serialized,
            user_line.main_user,
            user_line.main_line,
            user_line.user.tenant_uuid,
        )
        self._bus.queue_event(event)


def build_notifier():
    return UserLineNotifier(bus, sysconfd)
