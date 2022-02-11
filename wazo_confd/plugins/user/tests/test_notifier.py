# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import unittest
import uuid
from mock import Mock, call

from xivo_bus.resources.user.event import (
    CreateUserEvent,
    DeleteUserEvent,
    EditUserEvent,
    EditUserForwardEvent,
    EditUserServiceEvent,
)
from xivo_dao.alchemy.userfeatures import UserFeatures as User

from ..notifier import UserNotifier, UserServiceNotifier, UserForwardNotifier
from ..resource_sub import (
    ServiceDNDSchema,
    ServiceIncallFilterSchema,
    ForwardBusySchema,
    ForwardNoAnswerSchema,
    ForwardUnconditionalSchema,
    ForwardsSchema,
)


EXPECTED_HANDLERS = {
    'ipbx': [
        'dialplan reload',
        'module reload chan_sccp.so',
        'module reload app_queue.so',
        'module reload res_pjsip.so',
    ],
    'agentbus': [],
}


class TestUserNotifier(unittest.TestCase):
    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.user = Mock(
            User,
            id=1234,
            subscription_type=1,
            created_at=datetime.datetime.utcnow(),
            tenant_uuid=uuid.uuid4(),
        )
        self.expected_headers = {'tenant_uuid': str(self.user.tenant_uuid)}

        self.notifier = UserNotifier(self.sysconfd, self.bus)

    def test_when_user_created_then_sip_reloaded(self):
        self.notifier.created(self.user)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_user_created_then_event_sent_on_bus(self):
        expected_event = CreateUserEvent(
            self.user.id,
            self.user.uuid,
            subscription_type=self.user.subscription_type,
            created_at=self.user.created_at,
            tenant_uuid=self.user.tenant_uuid,
        )

        self.notifier.created(self.user)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_user_edited_then_sip_reloaded(self):
        self.notifier.edited(self.user)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_user_edited_then_event_sent_on_bus(self):
        expected_event = EditUserEvent(
            self.user.id,
            self.user.uuid,
            subscription_type=self.user.subscription_type,
            created_at=self.user.created_at,
            tenant_uuid=self.user.tenant_uuid,
        )

        self.notifier.edited(self.user)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )

    def test_when_user_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.user)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_user_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteUserEvent(
            self.user.id,
            self.user.uuid,
            subscription_type=self.user.subscription_type,
            created_at=self.user.created_at,
            tenant_uuid=self.user.tenant_uuid,
        )

        self.notifier.deleted(self.user)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=self.expected_headers
        )


class TestUserServiceNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.user = Mock(
            User,
            uuid='1234-abcd',
            tenant_uuid='5678-efgh',
            dnd_enabled=True,
            incallfilter_enabled=True,
        )

        self.notifier = UserServiceNotifier(self.bus)

    def test_when_user_service_dnd_edited_then_event_sent_on_bus(self):
        schema = ServiceDNDSchema()
        expected_event = EditUserServiceEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            schema.types[0],
            self.user.dnd_enabled,
        )
        expected_headers = {
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )

    def test_when_user_service_incallfilter_edited_then_event_sent_on_bus(self):
        schema = ServiceIncallFilterSchema()
        expected_event = EditUserServiceEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            schema.types[0],
            self.user.incallfilter_enabled,
        )
        expected_headers = {
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )


class TestUserForwardNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.user = Mock(
            User,
            id='1234',
            uuid='1234-abcd',
            tenant_uuid='5678-efgh',
            busy_enabled=True,
            busy_destination='123',
            noanswer_enabled=False,
            noanswer_destination='456',
            unconditional_enabled=True,
            unconditional_destination='789',
        )

        self.notifier = UserForwardNotifier(self.bus)

    def test_when_user_forward_busy_edited_then_event_sent_on_bus(self):
        schema = ForwardBusySchema()
        expected_event = EditUserForwardEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            'busy',
            self.user.busy_enabled,
            self.user.busy_destination,
        )
        expected_headers = {
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )

    def test_when_user_forward_noanswer_edited_then_event_sent_on_bus(self):
        schema = ForwardNoAnswerSchema()
        expected_event = EditUserForwardEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            'noanswer',
            self.user.noanswer_enabled,
            self.user.noanswer_destination,
        )
        expected_headers = {
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )

    def test_when_user_forward_unconditional_edited_then_event_sent_on_bus(self):
        schema = ForwardUnconditionalSchema()
        expected_event = EditUserForwardEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            'unconditional',
            self.user.unconditional_enabled,
            self.user.unconditional_destination,
        )
        expected_headers = {
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }
        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(
            expected_event, headers=expected_headers
        )

    def test_when_user_forwards_edited_then_event_sent_on_bus(self):
        schema = ForwardsSchema()
        self.notifier.edited(self.user, schema)

        expected_busy_event = EditUserForwardEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            'busy',
            self.user.busy_enabled,
            self.user.busy_destination,
        )
        expected_noanswer_event = EditUserForwardEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            'noanswer',
            self.user.noanswer_enabled,
            self.user.noanswer_destination,
        )
        expected_unconditional_event = EditUserForwardEvent(
            self.user.id,
            self.user.uuid,
            self.user.tenant_uuid,
            'unconditional',
            self.user.unconditional_enabled,
            self.user.unconditional_destination,
        )
        expected_headers = {
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }

        expected_calls = [
            call(expected_busy_event, headers=expected_headers),
            call(expected_noanswer_event, headers=expected_headers),
            call(expected_unconditional_event, headers=expected_headers),
        ]
        self.bus.send_bus_event.assert_has_calls(expected_calls)
