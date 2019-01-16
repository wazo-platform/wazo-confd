# -*- coding: utf-8 -*-
# Copyright 2013-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.user_line.event import UserLineAssociatedEvent, UserLineDissociatedEvent
from xivo_confd import bus, sysconfd


class UserLineNotifier(object):

    def __init__(self, bus, sysconfd):
        self._bus = bus
        self._sysconfd = sysconfd

    def _send_sysconfd_handlers(self):
        handlers = {
            'ctibus': [],
            'ipbx': ['dialplan reload', 'module reload res_pjsip.so'],
            'agentbus': [],
        }
        self._sysconfd.exec_request_handlers(handlers)

    def associated(self, user_line):
        self._send_sysconfd_handlers()
        event = UserLineAssociatedEvent(user_line.user_id,
                                        user_line.line_id,
                                        user_line.main_user,
                                        user_line.main_line)
        self._bus.send_bus_event(event)

    def dissociated(self, user_line):
        self._send_sysconfd_handlers()
        event = UserLineDissociatedEvent(user_line.user_id,
                                         user_line.line_id,
                                         user_line.main_user,
                                         user_line.main_line)
        self._bus.send_bus_event(event)


def build_notifier():
    return UserLineNotifier(bus, sysconfd)
