# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock
from uuid import uuid4

from xivo_bus.resources.outcall_trunk.event import OutcallTrunksAssociatedEvent
from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk

from ..notifier import OutcallTrunkNotifier


class TestOutcallTrunkNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.outcall = Mock(Outcall, id=2, tenant_uuid=uuid4())
        self.trunk = Mock(Trunk, id=1)

        self.notifier = OutcallTrunkNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = OutcallTrunksAssociatedEvent(
            self.outcall.id, [self.trunk.id], self.outcall.tenant_uuid
        )

        self.notifier.associated_all_trunks(self.outcall, [self.trunk])

        self.bus.queue_event.assert_called_once_with(expected_event)
