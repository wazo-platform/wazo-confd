# Copyright 2013-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid
from unittest.mock import Mock, patch

from wazo_bus.resources.user_line.event import (
    UserLineAssociatedEvent,
    UserLineDissociatedEvent,
)

from wazo_confd.plugins.endpoint_custom.schema import CustomSchema  # noqa
from wazo_confd.plugins.endpoint_sccp.resource import SccpSchema  # noqa
from wazo_confd.plugins.endpoint_sip.schema import EndpointSIPSchema  # noqa

from ..notifier import UserLineNotifier

EXPECTED_SYSCONFD_HANDLERS = {'ipbx': ['dialplan reload', 'module reload res_pjsip.so']}

USER_UUID = str(uuid.uuid4())
TENANT_UUID = str(uuid.uuid4())


class TestUserLineNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.user = Mock(uuid=USER_UUID, id=1, tenant_uuid=TENANT_UUID)
        self.serialized_user = {
            'uuid': self.user.uuid,
            'id': self.user.id,
            'tenant_uuid': self.user.tenant_uuid,
        }
        self.line = Mock(
            id=2,
            endpoint_sip={'uuid': str(uuid.uuid4())},
            endpoint_sccp=None,
            endpoint_custom=None,
        )
        self.line.name = 'limitation of mock instantiation with name ...'
        self.user_line = Mock(
            user=self.user, line=self.line, main_user=True, main_line=True
        )
        self.notifier = UserLineNotifier(self.bus, self.sysconfd)

    @patch('wazo_confd.plugins.user_line.notifier.UserSchema.dump')
    def test_associated_then_bus_event(self, user_dump):
        user_dump.return_value = self.serialized_user
        expected_event = UserLineAssociatedEvent(
            self.serialized_user,
            {
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            self.user_line.main_line,
            self.user_line.main_user,
            self.user.tenant_uuid,
        )

        self.notifier.associated(self.user_line)

        self.bus.queue_event.assert_called_once_with(expected_event)

    @patch('wazo_confd.plugins.user_line.notifier.UserSchema.dump')
    def test_associated_then_sip_reload(self, user_dump):
        user_dump.return_value = self.serialized_user
        self.notifier.associated(self.user_line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )

    @patch('wazo_confd.plugins.user_line.notifier.UserSchema.dump')
    def test_dissociated_then_bus_event(self, user_dump):
        user_dump.return_value = self.serialized_user
        expected_event = UserLineDissociatedEvent(
            self.serialized_user,
            {
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            self.user_line.main_line,
            self.user_line.main_user,
            self.user.tenant_uuid,
        )

        self.notifier.dissociated(self.user_line)

        self.bus.queue_event.assert_called_once_with(expected_event)

    @patch('wazo_confd.plugins.user_line.notifier.UserSchema.dump')
    def test_dissociated_then_sip_reload(self, user_dump):
        user_dump.return_value = self.serialized_user
        self.notifier.dissociated(self.user_line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )
