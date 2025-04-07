# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock

from wazo_bus.resources.endpoint_sccp.event import (
    SCCPEndpointCreatedEvent,
    SCCPEndpointDeletedEvent,
    SCCPEndpointEditedEvent,
)
from xivo_dao.alchemy.sccpline import SCCPLine as SCCP

from ..notifier import SccpEndpointNotifier

SYSCONFD_HANDLERS = {'ipbx': ['module reload chan_sccp.so', 'dialplan reload']}


class TestSccpEndpointNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.sccp = Mock(SCCP, id=1, tenant_uuid=str(uuid.uuid4), line={'id': 2})
        self.sccp_serialized = {
            'id': self.sccp.id,
            'tenant_uuid': self.sccp.tenant_uuid,
            'line': self.sccp.line,
        }
        self.expected_headers = {'tenant_uuid': self.sccp.tenant_uuid}

        self.notifier = SccpEndpointNotifier(self.sysconfd, self.bus)

    def test_when_sccp_endpoint_created_then_event_sent_on_bus(self):
        expected_event = SCCPEndpointCreatedEvent(
            self.sccp_serialized, self.sccp.tenant_uuid
        )

        self.notifier.created(self.sccp)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_sccp_endpoint_edited_then_sccp_reloaded(self):
        self.notifier.edited(self.sccp)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sccp_endpoint_edited_then_event_sent_on_bus(self):
        expected_event = SCCPEndpointEditedEvent(
            self.sccp_serialized, self.sccp.tenant_uuid
        )

        self.notifier.edited(self.sccp)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_sccp_endpoint_deleted_then_sccp_reloaded(self):
        self.notifier.deleted(self.sccp)

        self.sysconfd.exec_request_handlers.assert_called_once_with(SYSCONFD_HANDLERS)

    def test_when_sccp_endpoint_deleted_then_event_sent_on_bus(self):
        expected_event = SCCPEndpointDeletedEvent(
            self.sccp_serialized, self.sccp.tenant_uuid
        )

        self.notifier.deleted(self.sccp)

        self.bus.queue_event.assert_called_once_with(expected_event)
