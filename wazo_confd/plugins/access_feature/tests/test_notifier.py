# Copyright 2018-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from wazo_bus.resources.access_feature.event import (
    AccessFeatureCreatedEvent,
    AccessFeatureDeletedEvent,
    AccessFeatureEditedEvent,
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
        expected_event = AccessFeatureCreatedEvent(self.access_feature)

        self.notifier.created(self.access_feature)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_access_feature_edited_then_phoned_restarted(self):
        self.notifier.edited(self.access_feature)

        self.sysconfd.restart_phoned.assert_called_once()

    def test_when_access_feature_edited_then_event_sent_on_bus(self):
        expected_event = AccessFeatureEditedEvent(self.access_feature)

        self.notifier.edited(self.access_feature)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_access_feature_deleted_then_phoned_restarted(self):
        self.notifier.deleted(self.access_feature)

        self.sysconfd.restart_phoned.assert_called_once()

    def test_when_access_feature_deleted_then_event_sent_on_bus(self):
        expected_event = AccessFeatureDeletedEvent(self.access_feature)

        self.notifier.deleted(self.access_feature)

        self.bus.queue_event.assert_called_once_with(expected_event)
