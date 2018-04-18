# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user.event import (
    CreateUserEvent,
    DeleteUserEvent,
    EditUserEvent,
    EditUserForwardEvent,
    EditUserServiceEvent,
)

from xivo_confd import bus, sysconfd


class UserNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, action, user_id):
        cti_command = 'xivo[user,{},{}]'.format(action, user_id)
        handlers = {'ctibus': [cti_command],
                    'ipbx': ['dialplan reload',
                             'module reload chan_sccp.so',
                             'module reload app_queue.so',
                             'sip reload'],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, user):
        self.send_sysconfd_handlers('add', user.id)
        event = CreateUserEvent(
            user.id,
            user.uuid,
            subscription_type=user.subscription_type,
            created_at=user.created_at,
        )
        self.bus.send_bus_event(event)

    def edited(self, user):
        self.send_sysconfd_handlers('edit', user.id)
        event = EditUserEvent(
            user.id,
            user.uuid,
            subscription_type=user.subscription_type,
            created_at=user.created_at,
        )
        self.bus.send_bus_event(event)

    def deleted(self, user):
        self.send_sysconfd_handlers('delete', user.id)
        event = DeleteUserEvent(
            user.id,
            user.uuid,
            subscription_type=user.subscription_type,
            created_at=user.created_at,
        )
        self.bus.send_bus_event(event)


def build_notifier():
    return UserNotifier(sysconfd, bus)


class UserServiceNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def edited(self, user, schema):
        services = schema.dump(user).data
        for type_ in schema.types:
            service = services.get(type_, services)
            event = EditUserServiceEvent(user.uuid, type_, service['enabled'])
            self.bus.send_bus_event(event, headers={'user_uuid:{uuid}'.format(uuid=user.uuid): True})


def build_notifier_service():
    return UserServiceNotifier(bus)


class UserForwardNotifier(object):

    def __init__(self, bus):
        self.bus = bus

    def edited(self, user, schema):
        forwards = schema.dump(user).data
        for type_ in schema.types:
            forward = forwards.get(type_, forwards)
            event = EditUserForwardEvent(user.uuid, type_, forward['enabled'], forward['destination'])
            self.bus.send_bus_event(event, headers={'user_uuid:{uuid}'.format(uuid=user.uuid): True})


def build_notifier_forward():
    return UserForwardNotifier(bus)
