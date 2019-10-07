# Copyright 2013-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import uuid

from mock import Mock
from xivo_bus.resources.user_line.event import (
    UserLineAssociatedEvent,
    UserLineDissociatedEvent,
)

from ..notifier import UserLineNotifier

from wazo_confd.plugins.endpoint_custom.schema import CustomSchema  # noqa
from wazo_confd.plugins.endpoint_sccp.resource import SccpSchema  # noqa
from wazo_confd.plugins.endpoint_sip.schema import SipSchema  # noqa


EXPECTED_SYSCONFD_HANDLERS = {
    'ipbx': ['dialplan reload', 'module reload res_pjsip.so'],
    'agentbus': [],
}

USER_UUID = str(uuid.uuid4())
TENANT_UUID = str(uuid.uuid4())


class TestUserLineNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.sysconfd = Mock()
        self.user = Mock(uuid=USER_UUID, id=1, tenant_uuid=TENANT_UUID)
        self.line = Mock(
            id=2, endpoint_sip={'id': 3}, endpoint_sccp=None, endpoint_custom=None
        )
        self.line.name = 'limitation of mock instantiation with name ...'
        self.user_line = Mock(
            user=self.user, line=self.line, main_user=True, main_line=True
        )
        self.notifier = UserLineNotifier(self.bus, self.sysconfd)

    def test_associated_then_bus_event(self):
        expected_event = UserLineAssociatedEvent(
            user={
                'uuid': self.user.uuid,
                'id': self.user.id,
                'tenant_uuid': self.user.tenant_uuid,
            },
            line={
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            main_line=self.user_line.main_line,
            main_user=self.user_line.main_user,
        )

        self.notifier.associated(self.user_line)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_associated_then_sip_reload(self):
        self.notifier.associated(self.user_line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )

    def test_dissociated_then_bus_event(self):
        expected_event = UserLineDissociatedEvent(
            user={
                'uuid': self.user.uuid,
                'id': self.user.id,
                'tenant_uuid': self.user.tenant_uuid,
            },
            line={
                'id': self.line.id,
                'name': self.line.name,
                'endpoint_sip': self.line.endpoint_sip,
                'endpoint_sccp': self.line.endpoint_sccp,
                'endpoint_custom': self.line.endpoint_custom,
            },
            main_line=self.user_line.main_line,
            main_user=self.user_line.main_user,
        )

        self.notifier.dissociated(self.user_line)

        self.bus.send_bus_event.assert_called_once_with(expected_event)

    def test_dissociated_then_sip_reload(self):
        self.notifier.dissociated(self.user_line)

        self.sysconfd.exec_request_handlers.assert_called_once_with(
            EXPECTED_SYSCONFD_HANDLERS
        )
