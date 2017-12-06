# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.voicemail_general.event import EditVoicemailGeneralEvent


class VoicemailGeneralNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, voicemail_general):
        event = EditVoicemailGeneralEvent()
        self.bus.send_bus_event(event, event.routing_key)
        self.send_sysconfd_handlers(['voicemail reload'])


def build_notifier():
    return VoicemailGeneralNotifier(bus, sysconfd)
