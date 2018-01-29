# -*- coding: UTF-8 -*-
# Copyright 2017-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_bus.resources.sccp_general.event import EditSCCPGeneralEvent

from xivo_confd import bus, sysconfd


class SCCPGeneralNotifier(object):

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, sccp_general):
        event = EditSCCPGeneralEvent()
        self.bus.send_bus_event(event)
        self.send_sysconfd_handlers(['module reload chan_sccp.so'])


def build_notifier():
    return SCCPGeneralNotifier(bus, sysconfd)
