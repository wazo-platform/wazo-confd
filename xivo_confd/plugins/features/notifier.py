# -*- coding: utf-8 -*-
# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_bus.resources.features.event import (
    EditFeaturesApplicationmapEvent,
    EditFeaturesFeaturemapEvent,
    EditFeaturesGeneralEvent,
)

from xivo_confd import bus, sysconfd


class FeaturesConfigurationNotifier:

    def __init__(self, bus, sysconfd):
        self.bus = bus
        self.sysconfd = sysconfd

    def send_sysconfd_handlers(self, ipbx):
        handlers = {
            'ipbx': ipbx,
            'agentbus': [],
        }
        self.sysconfd.exec_request_handlers(handlers)

    def edited(self, section_name, features):
        if section_name == 'applicationmap':
            event = EditFeaturesApplicationmapEvent()
            self.bus.send_bus_event(event)
        elif section_name == 'featuremap':
            event = EditFeaturesFeaturemapEvent()
            self.bus.send_bus_event(event)
        elif section_name == 'general':
            event = EditFeaturesGeneralEvent()
            self.bus.send_bus_event(event)

        self.send_sysconfd_handlers(['module reload features'])


def build_notifier():
    return FeaturesConfigurationNotifier(bus, sysconfd)
