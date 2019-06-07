# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.trunk_register.event import (
    TrunkRegisterIAXAssociatedEvent,
    TrunkRegisterIAXDissociatedEvent,
    TrunkRegisterSIPAssociatedEvent,
    TrunkRegisterSIPDissociatedEvent,
)
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk

from ..notifier import TrunkRegisterIAXNotifier, TrunkRegisterSIPNotifier


class TestTrunkRegisterIAXNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.iax = Mock(id=2)
        self.trunk = Mock(Trunk, id=3)

        self.notifier_iax = TrunkRegisterIAXNotifier(self.bus)

    def test_associate_iax_then_bus_event(self):
        expected_event = TrunkRegisterIAXAssociatedEvent(self.trunk.id, self.iax.id)

        self.notifier_iax.associated(self.trunk, self.iax)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_iax_then_bus_event(self):
        expected_event = TrunkRegisterIAXDissociatedEvent(self.trunk.id, self.iax.id)

        self.notifier_iax.dissociated(self.trunk, self.iax)

        self.bus.send_bus_event.assert_called_once_with(expected_event)


class TestTrunkRegisterSIPNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sip = Mock(id=1)
        self.trunk = Mock(Trunk, id=3)

        self.notifier_sip = TrunkRegisterSIPNotifier(self.bus)

    def test_associate_sip_then_bus_event(self):
        expected_event = TrunkRegisterSIPAssociatedEvent(self.trunk.id, self.sip.id)

        self.notifier_sip.associated(self.trunk, self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_sip_then_bus_event(self):
        expected_event = TrunkRegisterSIPDissociatedEvent(self.trunk.id, self.sip.id)

        self.notifier_sip.dissociated(self.trunk, self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
