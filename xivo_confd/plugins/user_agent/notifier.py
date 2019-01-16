# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_agent.event import (
    UserAgentAssociatedEvent,
    UserAgentDissociatedEvent,
)

from xivo_confd import bus, sysconfd


class UserAgentNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ctibus_command):
        handlers = {'ctibus': [ctibus_command],
                    'ipbx': [],
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def associated(self, user, agent):
        ctibus_command = 'xivo[user,edit,{user_id}]'.format(user_id=user.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = UserAgentAssociatedEvent(user.uuid, agent.id)
        self.bus.send_bus_event(event)

    def dissociated(self, user, agent):
        ctibus_command = 'xivo[user,edit,{user_id}]'.format(user_id=user.id)
        self.send_sysconfd_handlers(ctibus_command)
        event = UserAgentDissociatedEvent(user.uuid, agent.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return UserAgentNotifier(bus, sysconfd)
