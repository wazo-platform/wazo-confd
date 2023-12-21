# Copyright 2015-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from xivo_bus.resources.endpoint_sip.event import (
    SIPEndpointCreatedEvent,
    SIPEndpointDeletedEvent,
    SIPEndpointEditedEvent,
    SIPEndpointTemplateCreatedEvent,
    SIPEndpointTemplateDeletedEvent,
    SIPEndpointTemplateEditedEvent,
)

from ..notifier import SipEndpointNotifier, SipTemplateNotifier

SYSCONFD_HANDLERS = {'ipbx': ['module reload res_pjsip.so', 'dialplan reload']}


class TestSipEndpointNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sip = Mock(
            uuid=str(uuid.uuid4()),
            tenant_uuid=str(uuid.uuid4()),
            label='label',
            auth_section_options=[['username', 'username']],
            registration_section_options=[['client_uri', 'client_uri']],
            trunk={'id': 2},
            line=None,
        )
        self.sip.name = 'limitation of mock instantiation with name ...'
        self.sip_serialized = {
            'uuid': self.sip.uuid,
            'tenant_uuid': self.sip.tenant_uuid,
            'name': self.sip.name,
            'auth_section_options': self.sip.auth_section_options,
            'registration_section_options': self.sip.registration_section_options,
            'label': self.sip.label,
            'trunk': self.sip.trunk,
            'line': self.sip.line,
        }
        self.notifier = SipEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sip_endpoint_created_then_event_sent_on_bus(self):
        expected_event = SIPEndpointCreatedEvent(
            self.sip_serialized, self.sip.tenant_uuid
        )

        self.notifier.created(self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_sip_endpoint_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = SIPEndpointEditedEvent(
            self.sip_serialized, self.sip.tenant_uuid
        )

        self.notifier.edited(self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_sip_endpoint_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = SIPEndpointDeletedEvent(
            self.sip_serialized, self.sip.tenant_uuid
        )

        self.notifier.deleted(self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)


class TestSipTemplateNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sip = Mock(
            tenant_uuid=str(uuid.uuid4()),
        )
        self.expected_headers = {'tenant_uuid': self.sip.tenant_uuid}
        self.notifier = SipTemplateNotifier(self.sysconfd, self.bus)

    def test_when_sip_template_created_then_event_sent_on_bus(self):
        expected_event = SIPEndpointTemplateCreatedEvent({}, self.sip.tenant_uuid)

        self.notifier.created(self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_sip_template_edited_then_sip_reloaded(self):
        self.notifier.edited(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_template_edited_then_event_sent_on_bus(self):
        expected_event = SIPEndpointTemplateEditedEvent({}, self.sip.tenant_uuid)

        self.notifier.edited(self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_sip_template_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.sip)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sip_template_deleted_then_event_sent_on_bus(self):
        expected_event = SIPEndpointTemplateDeletedEvent({}, self.sip.tenant_uuid)

        self.notifier.deleted(self.sip)

        self.bus.queue_event.assert_called_once_with(expected_event)
