# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from mock import Mock

from xivo_bus.resources.access_feature.event import (
    CreateAccessFeatureEvent,
    DeleteAccessFeatureEvent,
    EditAccessFeatureEvent,
)

from ..notifier import AccessFeatureNotifier


class TestAccessFeatureNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.access_feature = {'id': 123}

        self.notifier = AccessFeatureNotifier(self.bus, self.sysconfd)

    def test_when_access_feature_created_then_phoned_restarted(self):
        self.notifier.created(self.access_feature)

        self.sysconfd.restart_phoned.assert_called_once()

    def test_when_access_feature_created_then_event_sent_on_bus(self):
        expected_event = CreateAccessFeatureEvent(self.access_feature)

        self.notifier.created(self.access_feature)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_access_feature_edited_then_phoned_restarted(self):
        self.notifier.edited(self.access_feature)

        self.sysconfd.restart_phoned.assert_called_once()

    def test_when_access_feature_edited_then_event_sent_on_bus(self):
        expected_event = EditAccessFeatureEvent(self.access_feature)

        self.notifier.edited(self.access_feature)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_when_access_feature_deleted_then_phoned_restarted(self):
        self.notifier.deleted(self.access_feature)

        self.sysconfd.restart_phoned.assert_called_once()

    def test_when_access_feature_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteAccessFeatureEvent(self.access_feature)

        self.notifier.deleted(self.access_feature)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
