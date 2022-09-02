# Copyright 2015-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import datetime
import unittest
import uuid
from unittest.mock import Mock, call
from hamcrest import assert_that, has_entries

from xivo_bus.resources.user.event import (
    UserCreatedEvent,
    UserDeletedEvent,
    UserEditedEvent,
    UserForwardEditedEvent,
    UserServiceEditedEvent,
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
    ]
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

        self.notifier = UserNotifier(self.sysconfd, self.bus)

    def test_when_user_created_then_sip_reloaded(self):
        self.notifier.created(self.user)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_user_created_then_event_sent_on_bus(self):
        expected_event = UserCreatedEvent(
            self.user.id,
            self.user.uuid,
            self.user.subscription_type,
            self.user.created_at,
            self.user.tenant_uuid,
        )

        self.notifier.created(self.user)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_user_edited_then_sip_reloaded(self):
        self.notifier.edited(self.user)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_user_edited_then_event_sent_on_bus(self):
        expected_event = UserEditedEvent(
            self.user.id,
            self.user.uuid,
            self.user.subscription_type,
            self.user.created_at,
            self.user.tenant_uuid,
        )

        self.notifier.edited(self.user)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_user_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.user)

        self.sysconfd.exec_request_handlers.assert_called_once_with(EXPECTED_HANDLERS)

    def test_when_user_deleted_then_event_sent_on_bus(self):
        expected_event = UserDeletedEvent(
            self.user.id,
            self.user.uuid,
            self.user.subscription_type,
            self.user.created_at,
            self.user.tenant_uuid,
        )

        self.notifier.deleted(self.user)

        self.bus.queue_event.assert_called_once_with(expected_event)


class TestUserServiceNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.user = Mock(
            User,
            id=1234,
            uuid='1234-abcd',
            tenant_uuid='5678-efgh',
            dnd_enabled=True,
            incallfilter_enabled=True,
        )

        self.notifier = UserServiceNotifier(self.bus)

    def test_when_user_service_dnd_edited_then_event_sent_on_bus(self):
        schema = ServiceDNDSchema()
        expected_event = UserServiceEditedEvent(
            self.user.id,
            schema.types[0],
            self.user.dnd_enabled,
            self.user.tenant_uuid,
            self.user.uuid,
        )

        self.notifier.edited(self.user, schema)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_user_service_incallfilter_edited_then_event_sent_on_bus(self):
        schema = ServiceIncallFilterSchema()
        expected_event = UserServiceEditedEvent(
            self.user.id,
            schema.types[0],
            self.user.incallfilter_enabled,
            self.user.tenant_uuid,
            self.user.uuid,
        )

        self.notifier.edited(self.user, schema)

        self.bus.queue_event.assert_called_once_with(expected_event)


class TestUserForwardNotifier(unittest.TestCase):
    def setUp(self):
        self.bus = Mock()
        self.user = Mock(
            User,
            id=1234,
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
        expected_event = UserForwardEditedEvent(
            self.user.id,
            'busy',
            self.user.busy_enabled,
            self.user.busy_destination,
            self.user.tenant_uuid,
            self.user.uuid,
        )

        expected_headers = {
            'name': expected_event.name,
            'tenant_uuid': self.user.tenant_uuid,
            f'user_uuid:{self.user.uuid}': True,
        }
        assert_that(expected_event.headers, has_entries(**expected_headers))

        self.notifier.edited(self.user, schema)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_user_forward_noanswer_edited_then_event_sent_on_bus(self):
        schema = ForwardNoAnswerSchema()
        expected_event = UserForwardEditedEvent(
            self.user.id,
            'noanswer',
            self.user.noanswer_enabled,
            self.user.noanswer_destination,
            self.user.tenant_uuid,
            self.user.uuid,
        )

        expected_headers = {
            'name': expected_event.name,
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }
        assert_that(expected_event.headers, has_entries(expected_headers))

        self.notifier.edited(self.user, schema)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_user_forward_unconditional_edited_then_event_sent_on_bus(self):
        schema = ForwardUnconditionalSchema()
        expected_event = UserForwardEditedEvent(
            self.user.id,
            'unconditional',
            self.user.unconditional_enabled,
            self.user.unconditional_destination,
            self.user.tenant_uuid,
            self.user.uuid,
        )

        expected_headers = {
            'name': expected_event.name,
            f'user_uuid:{self.user.uuid}': True,
            'tenant_uuid': self.user.tenant_uuid,
        }
        assert_that(expected_event.headers, has_entries(expected_headers))

        self.notifier.edited(self.user, schema)

        self.bus.queue_event.assert_called_once_with(expected_event)

    def test_when_user_forwards_edited_then_event_sent_on_bus(self):
        schema = ForwardsSchema()
        self.notifier.edited(self.user, schema)

        expected_busy_event = UserForwardEditedEvent(
            self.user.id,
            'busy',
            self.user.busy_enabled,
            self.user.busy_destination,
            self.user.tenant_uuid,
            self.user.uuid,
        )
        expected_noanswer_event = UserForwardEditedEvent(
            self.user.id,
            'noanswer',
            self.user.noanswer_enabled,
            self.user.noanswer_destination,
            self.user.tenant_uuid,
            self.user.uuid,
        )
        expected_unconditional_event = UserForwardEditedEvent(
            self.user.id,
            'unconditional',
            self.user.unconditional_enabled,
            self.user.unconditional_destination,
            self.user.tenant_uuid,
            self.user.uuid,
        )

        for event in (
            expected_busy_event,
            expected_noanswer_event,
            expected_unconditional_event,
        ):
            expected_headers = {
                'name': event.name,
                f'user_uuid:{self.user.uuid}': True,
                'tenant_uuid': self.user.tenant_uuid,
            }
            assert_that(event.headers, has_entries(expected_headers))

        expected_calls = [
            call(expected_busy_event),
            call(expected_noanswer_event),
            call(expected_unconditional_event),
        ]
        self.bus.queue_event.assert_has_calls(expected_calls)
