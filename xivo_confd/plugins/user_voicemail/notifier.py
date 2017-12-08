# -*- coding: utf-8 -*-
# Copyright 2013-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.user_voicemail.event import (
    UserVoicemailAssociatedEvent,
    UserVoicemailDissociatedEvent,
)
from xivo_confd import bus, sysconfd


class UserVoicemailNotifier(object):

    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def _send_sysconfd_handlers(self, cti_commands):
        handlers = {
            'ctibus': cti_commands,
            'ipbx': ['sip reload', 'module reload chan_sccp.so'],
            'agentbus': [],
        }
        self._sysconfd.exec_request_handlers(handlers)

    def _generate_cti_commands(self, user):
        ctibus = ['xivo[user,edit,{}]'.format(user.id)]

        for line in user.lines:
            ctibus.append('xivo[phone,edit,{}]'.format(line.id))

        return ctibus

    def associated(self, user, voicemail):
        cti_commands = self._generate_cti_commands(user)
        self._send_sysconfd_handlers(cti_commands)
        event = UserVoicemailAssociatedEvent(user.uuid, voicemail.id)
        self._bus.send_bus_event(event, event.routing_key)

    def dissociated(self, user, voicemail):
        cti_commands = self._generate_cti_commands(user)
        self._send_sysconfd_handlers(cti_commands)
        event = UserVoicemailDissociatedEvent(user.uuid, voicemail.id)
        self._bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return UserVoicemailNotifier(bus, sysconfd)
