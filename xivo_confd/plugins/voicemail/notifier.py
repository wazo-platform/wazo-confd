# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.voicemail.event import (CreateVoicemailEvent,
                                                EditVoicemailEvent,
                                                EditUserVoicemailEvent,
                                                DeleteVoicemailEvent)


class VoicemailNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def _send_sysconfd_handlers(self, ctibus_command, ipbx_commands):
        handlers = {
            'ctibus': [ctibus_command],
            'ipbx': ipbx_commands,
            'agentbus': []
        }
        self.sysconfd.exec_request_handlers(handlers)

    def created(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,add,%s]' % voicemail.id,
                                     ['voicemail reload'])
        event = CreateVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event, event.routing_key)

    def edited(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,edit,%s]' % voicemail.id,
                                     ['voicemail reload',
                                      'sip reload',
                                      'module reload chan_sccp.so'])
        event = EditVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event, event.routing_key)
        for user in voicemail.users:
            event = EditUserVoicemailEvent(user.uuid, voicemail.id)
            self.bus.send_bus_event(event, event.routing_key)

    def deleted(self, voicemail):
        self._send_sysconfd_handlers('xivo[voicemail,delete,%s]' % voicemail.id,
                                     ['voicemail reload'])
        event = DeleteVoicemailEvent(voicemail.id)
        self.bus.send_bus_event(event, event.routing_key)


def build_notifier():
    return VoicemailNotifier(bus, sysconfd)
