# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import Mock

from xivo_bus.resources.outcall_trunk.event import OutcallTrunksAssociatedEvent
from ..notifier import OutcallTrunkNotifier

from xivo_dao.alchemy.outcall import Outcall
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk


class TestOutcallTrunkNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.outcall = Mock(Outcall, id=2)
        self.trunk = Mock(Trunk, id=1)

        self.notifier = OutcallTrunkNotifier(self.bus)

    def test_associate_then_bus_event(self):
        expected_event = OutcallTrunksAssociatedEvent(self.outcall.id, [self.trunk.id])

        self.notifier.associated_all_trunks(self.outcall, [self.trunk])

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)
