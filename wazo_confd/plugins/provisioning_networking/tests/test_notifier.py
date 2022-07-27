# Copyright 2019-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from unittest.mock import Mock
from xivo_bus.resources.provisioning_networking.event import (
    ProvisioningNetworkingEditedEvent,
)

from ..notifier import ProvisioningNetworkingNotifier


class TestProvisioningNetworkingNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.notifier = ProvisioningNetworkingNotifier(self.bus, self.sysconfd)

    def test_when_provisioning_networking_edited_then_event_sent_on_bus(self):
        expected_event = ProvisioningNetworkingEditedEvent()
        provisioning_networking = {
            'provision_host': '1.2.3.4',
            'provision_http_port': 8666,
            'rest_host': '2.3.4.5',
            'rest_https_port': 8667,
        }

        self.notifier.edited(provisioning_networking)

        self.bus.queue_event.assert_called_once_with(expected_event)
        self.sysconfd.restart_provd.assert_called_once_with()
