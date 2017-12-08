# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_cti_profile.event import UserCtiProfileEditedEvent
from xivo_confd import bus, sysconfd


class UserCtiProfileNotifier(object):

    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def _send_sysconfd_handlers(self, cti_command):
        handlers = {
            'ctibus': cti_command,
            'ipbx': [],
            'agentbus': [],
        }
        self._sysconfd.exec_request_handlers(handlers)

    def _generate_cti_commands(self, user_id):
        return ['xivo[user,edit,%d]' % user_id]

    def edited(self, user):
        cti_command = self._generate_cti_commands(user.id)
        self._send_sysconfd_handlers(cti_command)

        event = UserCtiProfileEditedEvent(user.id, user.cti_profile_id, user.cti_enabled)
        self._bus.send_bus_event(event)


def build_notifier():
    return UserCtiProfileNotifier(bus, sysconfd)
