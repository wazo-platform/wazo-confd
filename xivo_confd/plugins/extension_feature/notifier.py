# -*- coding: UTF-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_confd import bus, sysconfd

from xivo_bus.resources.extension_feature.event import (
    EditExtensionFeatureEvent,
)


class ExtensionFeatureNotifier(object):

    def __init__(self, sysconfd, bus):
        self.sysconfd = sysconfd
        self.bus = bus

    def send_sysconfd_handlers(self, ipbx):
        handlers = {'ctibus': [],
                    'ipbx': ipbx,
                    'agentbus': []}
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, extension):
        self.send_sysconfd_handlers(['dialplan reload'])
        event = EditExtensionFeatureEvent(extension.id)
        self.bus.send_bus_event(event)


def build_notifier():
    return ExtensionFeatureNotifier(sysconfd, bus)
