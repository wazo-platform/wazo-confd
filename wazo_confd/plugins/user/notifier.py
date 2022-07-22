# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user.event import (
    UserCreatedEvent,
    UserDeletedEvent,
    UserEditedEvent,
    UserForwardEditedEvent,
    UserServiceEditedEvent,
)

from wazo_confd import bus, sysconfd


class UserNotifier:
    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self):
        handlers = {
            'ipbx': [
                'dialplan reload',
                'module reload chan_sccp.so',
                'module reload app_queue.so',
                'module reload res_pjsip.so',
            ],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, user):
        self.send_sysconfd_handlers()
        event = UserCreatedEvent(
            user.id,
            user.uuid,
            user.subscription_type,
            user.created_at,
            user.tenant_uuid,
        )
        self.bus.send_bus_event(event)

    def edited(self, user):
        self.send_sysconfd_handlers()
        event = UserEditedEvent(
            user.id,
            user.uuid,
            user.subscription_type,
            user.created_at,
            user.tenant_uuid,
        )
        self.bus.send_bus_event(event)

    def deleted(self, user):
        self.send_sysconfd_handlers()
        event = UserDeletedEvent(
            user.id,
            user.uuid,
            user.subscription_type,
            user.created_at,
            user.tenant_uuid,
        )
        self.bus.send_bus_event(event)


def build_notifier():
    return UserNotifier(sysconfd, bus)


class UserServiceNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, user, schema):
        services = schema.dump(user)
        for type_ in schema.types:
            service = services.get(type_, services)
            event = UserServiceEditedEvent(
                user.id, type_, service['enabled'], user.tenant_uuid, user.uuid
            )
            self.bus.send_bus_event(event)


def build_notifier_service():
    return UserServiceNotifier(bus)


class UserForwardNotifier:
    def __init__(self, bus):
        self.bus = bus

    def edited(self, user, schema):
        forwards = schema.dump(user)
        for type_ in schema.types:
            forward = forwards.get(type_, forwards)
            event = UserForwardEditedEvent(
                user.id,
                type_,
                forward['enabled'],
                forward['destination'],
                user.tenant_uuid,
                user.uuid,
            )

            self.bus.send_bus_event(event)


def build_notifier_forward():
    return UserForwardNotifier(bus)
