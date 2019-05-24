# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.voicemail_general.event import EditVoicemailGeneralEvent

from xivo_confd import bus, sysconfd


class VoicemailGeneralNotifier:

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {
            'ipbx': ipbx,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, voicemail_general):
        event = EditVoicemailGeneralEvent()
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['voicemail reload'])


def build_notifier():
    return VoicemailGeneralNotifier(bus, sysconfd)
