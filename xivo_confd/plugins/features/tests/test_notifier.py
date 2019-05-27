# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.features.event import (
    EditFeaturesApplicationmapEvent,
    EditFeaturesFeaturemapEvent,
    EditFeaturesGeneralEvent,
)

from ..notifier import FeaturesConfigurationNotifier


SYSCONFD_HANDLERS = {
    'ipbx': ['module reload features'],
    'agentbus': [],
}


class TestFeaturesConfigurationNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.features = Mock()
        self.sysconfd = Mock()

        self.notifier = FeaturesConfigurationNotifier(self.bus, self.sysconfd)

    def test_when_features_applicationmap_edited_then_event_sent_on_bus(self):
        expected_event = EditFeaturesApplicationmapEvent()

        self.notifier.edited('applicationmap', self.features)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_features_applicationmap_edited_then_sip_reloaded(self):
        self.notifier.edited('applicationmap', self.features)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_features_featuremap_edited_then_event_sent_on_bus(self):
        expected_event = EditFeaturesFeaturemapEvent()

        self.notifier.edited('featuremap', self.features)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_features_featuremap_edited_then_sip_reloaded(self):
        self.notifier.edited('featuremap', self.features)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_features_general_edited_then_event_sent_on_bus(self):
        expected_event = EditFeaturesGeneralEvent()

        self.notifier.edited('general', self.features)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_features_general_edited_then_sip_reloaded(self):
        self.notifier.edited('general', self.features)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)
