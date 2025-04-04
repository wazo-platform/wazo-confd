# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from wazo_bus.resources.trunk_endpoint.event import (
    TrunkEndpointCustomAssociatedEvent,
    TrunkEndpointCustomDissociatedEvent,
    TrunkEndpointIAXAssociatedEvent,
    TrunkEndpointIAXDissociatedEvent,
    TrunkEndpointSIPAssociatedEvent,
    TrunkEndpointSIPDissociatedEvent,
)
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk
from xivo_dao.alchemy.usercustom import UserCustom as Custom
from xivo_dao.alchemy.useriax import UserIAX as IAX

from ..notifier import (
    TrunkEndpointCustomNotifier,
    TrunkEndpointIAXNotifier,
    TrunkEndpointSIPNotifier,
)


class TestTrunkEndpointNotifier(unittest.TestCase):
    def setUp(self):
        tenant_uuid = str(uuid.uuid4())
        self.bus = Mock()
        self.sysconfd = Mock()
        self.sip = Mock(
            uuid=str(uuid.uuid4()),
            auth_section_options=[['username', 'username']],
            registration_section_options=[['client_uri', 'client-uri']],
            tenant_uuid=tenant_uuid,
        )
        self.sip.name = 'limitation of mock instantiation with name ...'
        self.custom = Mock(Custom, id=2, tenant_uuid=tenant_uuid, interface='custom')
        self.iax = Mock(IAX, id=3, tenant_uuid=tenant_uuid)
        self.iax.name = 'limitation of mock instantiation with name ...'
        self.trunk = Mock(Trunk, id=4, tenant_uuid=tenant_uuid)

        self.notifier_custom = TrunkEndpointCustomNotifier(self.bus, self.sysconfd)
        self.notifier_sip = TrunkEndpointSIPNotifier(self.bus, self.sysconfd)
        self.notifier_iax = TrunkEndpointIAXNotifier(self.bus, self.sysconfd)

    def test_associate_sip_then_bus_event(self):
        expected_event = TrunkEndpointSIPAssociatedEvent(
            {'id': self.trunk.id, 'tenant_uuid': self.trunk.tenant_uuid},
            {
                'uuid': self.sip.uuid,
                'tenant_uuid': self.sip.tenant_uuid,
                'name': self.sip.name,
                'auth_section_options': self.sip.auth_section_options,
                'registration_section_options': self.sip.registration_section_options,
            },
            self.trunk.tenant_uuid,
        )

        self.notifier_sip.associated(self.trunk, self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_custom_then_bus_event(self):
        expected_event = TrunkEndpointCustomAssociatedEvent(
            {'id': self.trunk.id, 'tenant_uuid': self.trunk.tenant_uuid},
            {
                'id': self.custom.id,
                'tenant_uuid': self.custom.tenant_uuid,
                'interface': self.custom.interface,
            },
            self.trunk.tenant_uuid,
        )

        self.notifier_custom.associated(self.trunk, self.custom)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_iax_then_bus_event(self):
        expected_event = TrunkEndpointIAXAssociatedEvent(
            {'id': self.trunk.id, 'tenant_uuid': self.trunk.tenant_uuid},
            {
                'id': self.iax.id,
                'tenant_uuid': self.iax.tenant_uuid,
                'name': self.iax.name,
            },
            self.trunk.tenant_uuid,
        )

        self.notifier_iax.associated(self.trunk, self.iax)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_associate_sip_then_sysconfd_event(self):
        self.notifier_sip.associated(self.trunk, self.sip)
        expected = {'ipbx': ['module reload res_pjsip.so']}

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected)

    def test_associate_custom_then_no_sysconfd_event(self):
        self.notifier_custom.associated(self.trunk, self.custom)

        self.sysconfd.exec_request_handlers.assert_not_called()

    def test_associate_iax_then_sysconfd_event(self):
        self.notifier_iax.associated(self.trunk, self.iax)
        expected = {'ipbx': ['iax2 reload']}

        self.sysconfd.exec_request_handlers.assert_called_once_with(expected)

    def test_dissociate_sip_then_bus_event(self):
        expected_event = TrunkEndpointSIPDissociatedEvent(
            {'id': self.trunk.id, 'tenant_uuid': self.trunk.tenant_uuid},
            {
                'uuid': self.sip.uuid,
                'tenant_uuid': self.sip.tenant_uuid,
                'name': self.sip.name,
                'auth_section_options': self.sip.auth_section_options,
                'registration_section_options': self.sip.registration_section_options,
            },
            self.trunk.tenant_uuid,
        )

        self.notifier_sip.dissociated(self.trunk, self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_custom_then_bus_event(self):
        expected_event = TrunkEndpointCustomDissociatedEvent(
            {'id': self.trunk.id, 'tenant_uuid': self.trunk.tenant_uuid},
            {
                'id': self.custom.id,
                'tenant_uuid': self.custom.tenant_uuid,
                'interface': self.custom.interface,
            },
            self.trunk.tenant_uuid,
        )

        self.notifier_custom.dissociated(self.trunk, self.custom)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_dissociate_iax_then_bus_event(self):
        expected_event = TrunkEndpointIAXDissociatedEvent(
            {'id': self.trunk.id, 'tenant_uuid': self.trunk.tenant_uuid},
            {
                'id': self.iax.id,
                'tenant_uuid': self.iax.tenant_uuid,
                'name': self.iax.name,
            },
            self.trunk.tenant_uuid,
        )

        self.notifier_iax.dissociated(self.trunk, self.iax)

        self.bus.queue_event.assert_called_once_with(expected_event)
