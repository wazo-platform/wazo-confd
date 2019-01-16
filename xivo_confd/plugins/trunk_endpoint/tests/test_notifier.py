# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from mock import Mock

from xivo_bus.resources.trunk_endpoint.event import (
    TrunkEndpointAssociatedEvent,
    TrunkEndpointDissociatedEvent,
)
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.alchemy.usersip import UserSIP as Sip
from xivo_dao.alchemy.useriax import UserIAX as IAX

from ..notifier import TrunkEndpointNotifier


class TestTrunkEndpointNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.sip = Mock(Sip, id=1)
        self.custom = Mock(Custom, id=2)
        self.iax = Mock(IAX, id=3)
        self.trunk = Mock(Trunk, id=4)

        self.notifier_custom = TrunkEndpointNotifier('custom', self.bus, self.sysconfd)
        self.notifier_sip = TrunkEndpointNotifier('sip', self.bus, self.sysconfd)
        self.notifier_iax = TrunkEndpointNotifier('iax', self.bus, self.sysconfd)

    def test_associate_sip_then_bus_event(self):
        expected_event = TrunkEndpointAssociatedEvent(self.trunk.id, self.sip.id)

        self.notifier_sip.associated(self.trunk, self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_custom_then_bus_event(self):
        expected_event = TrunkEndpointAssociatedEvent(self.trunk.id, self.custom.id)

        self.notifier_custom.associated(self.trunk, self.custom)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_iax_then_bus_event(self):
        expected_event = TrunkEndpointAssociatedEvent(self.trunk.id, self.iax.id)

        self.notifier_iax.associated(self.trunk, self.iax)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associate_sip_then_sysconfd_event(self):
        self.notifier_sip.associated(self.trunk, self.sip)
        expected = {'ctibus': [],
                    'ipbx': ['module reload res_pjsip.so'],
                    'agentbus': []}

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected)

    def test_associate_custom_then_no_sysconfd_event(self):
        self.notifier_custom.associated(self.trunk, self.custom)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_associate_iax_then_sysconfd_event(self):
        self.notifier_iax.associated(self.trunk, self.iax)
        expected = {'ctibus': [],
                    'ipbx': ['iax2 reload'],
                    'agentbus': []}

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected)

    def test_dissociate_sip_then_bus_event(self):
        expected_event = TrunkEndpointDissociatedEvent(self.trunk.id, self.sip.id)

        self.notifier_sip.dissociated(self.trunk, self.sip)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_custom_then_bus_event(self):
        expected_event = TrunkEndpointDissociatedEvent(self.trunk.id, self.custom.id)

        self.notifier_custom.dissociated(self.trunk, self.custom)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociate_iax_then_bus_event(self):
        expected_event = TrunkEndpointDissociatedEvent(self.trunk.id, self.iax.id)

        self.notifier_iax.dissociated(self.trunk, self.iax)

        self.bus.send_bus_event.assert_called_once_with(expected_event)
