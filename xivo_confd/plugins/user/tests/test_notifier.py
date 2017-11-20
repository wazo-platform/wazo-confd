# -*- coding: utf-8 -*-
# Copyright 2015-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import unittest
from mock import Mock, call

from xivo_bus.resources.user.event import (CreateUserEvent,
                                           EditUserEvent,
                                           DeleteUserEvent,
                                           EditUserServiceEvent,
                                           EditUserForwardEvent)
from xivo_confd.plugins.user.notifier import UserNotifier, UserServiceNotifier, UserForwardNotifier
from xivo_confd.plugins.user.resource_sub import (ServiceDNDSchema,
                                                  ServiceIncallFilterSchema,
                                                  ForwardBusySchema,
                                                  ForwardNoAnswerSchema,
                                                  ForwardUnconditionalSchema,
                                                  ForwardsSchema)

from xivo_dao.alchemy.userfeatures import UserFeatures as User


def sysconfd_handler(action, user_id):
    cti = 'xivo[user,{},{}]'.format(action, user_id)
    return {'ctibus': [cti],
            'ipbx': ['dialplan reload',
                     'module reload chan_sccp.so',
                     'module reload app_queue.so',
                     'sip reload'],
            'agentbus': []}


class TestUserNotifier(unittest.TestCase):

    def setUp(self):
        self.sysconfd = Mock()
        self.bus = Mock()
        self.user = Mock(User, id=1234)

        self.notifier = UserNotifier(self.sysconfd, self.bus)

    def test_when_user_created_then_sip_reloaded(self):
        self.notifier.created(self.user)

        handler = sysconfd_handler('add', self.user.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(handler)

    def test_when_user_created_then_event_sent_on_bus(self):
        expected_event = CreateUserEvent(self.user.id, self.user.uuid)

        self.notifier.created(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_user_edited_then_sip_reloaded(self):
        self.notifier.edited(self.user)

        handler = sysconfd_handler('edit', self.user.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(handler)

    def test_when_user_edited_then_event_sent_on_bus(self):
        expected_event = EditUserEvent(self.user.id, self.user.uuid)

        self.notifier.edited(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)

    def test_when_user_deleted_then_sip_reloaded(self):
        self.notifier.deleted(self.user)

        handler = sysconfd_handler('delete', self.user.id)
        self.sysconfd.exec_request_handlers.assert_called_once_with(handler)

    def test_when_user_deleted_then_event_sent_on_bus(self):
        expected_event = DeleteUserEvent(self.user.id, self.user.uuid)

        self.notifier.deleted(self.user)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key)


class TestUserServiceNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user = Mock(User, uuid='1234-abcd', dnd_enabled=True, incallfilter_enabled=True)

        self.notifier = UserServiceNotifier(self.bus)

    def test_when_user_service_dnd_edited_then_event_sent_on_bus(self):
        schema = ServiceDNDSchema()
        expected_event = EditUserServiceEvent(self.user.uuid,
                                              schema.types[0],
                                              self.user.dnd_enabled)

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key,
                                                        headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True})

    def test_when_user_service_incallfilter_edited_then_event_sent_on_bus(self):
        schema = ServiceIncallFilterSchema()
        expected_event = EditUserServiceEvent(self.user.uuid,
                                              schema.types[0],
                                              self.user.incallfilter_enabled)

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key,
                                                        headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True})


class TestUserForwardNotifier(unittest.TestCase):

    def setUp(self):
        self.bus = Mock()
        self.user = Mock(User, uuid='1234-abcd',
                         busy_enabled=True, busy_destination='123',
                         noanswer_enabled=False, noanswer_destination='456',
                         unconditional_enabled=True, unconditional_destination='789')

        self.notifier = UserForwardNotifier(self.bus)

    def test_when_user_forward_busy_edited_then_event_sent_on_bus(self):
        schema = ForwardBusySchema()
        expected_event = EditUserForwardEvent(self.user.uuid,
                                              'busy',
                                              self.user.busy_enabled,
                                              self.user.busy_destination)

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key,
                                                        headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True})

    def test_when_user_forward_noanswer_edited_then_event_sent_on_bus(self):
        schema = ForwardNoAnswerSchema()
        expected_event = EditUserForwardEvent(self.user.uuid,
                                              'noanswer',
                                              self.user.noanswer_enabled,
                                              self.user.noanswer_destination)

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key,
                                                        headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True})

    def test_when_user_forward_unconditional_edited_then_event_sent_on_bus(self):
        schema = ForwardUnconditionalSchema()
        expected_event = EditUserForwardEvent(self.user.uuid,
                                              'unconditional',
                                              self.user.unconditional_enabled,
                                              self.user.unconditional_destination)

        self.notifier.edited(self.user, schema)

        self.bus.send_bus_event.assert_called_once_with(expected_event,
                                                        expected_event.routing_key,
                                                        headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True})

    def test_when_user_forwards_edited_then_event_sent_on_bus(self):
        schema = ForwardsSchema()
        self.notifier.edited(self.user, schema)

        expected_busy_event = EditUserForwardEvent(self.user.uuid,
                                                   'busy',
                                                   self.user.busy_enabled,
                                                   self.user.busy_destination)

        expected_noanswer_event = EditUserForwardEvent(self.user.uuid,
                                                       'noanswer',
                                                       self.user.noanswer_enabled,
                                                       self.user.noanswer_destination)
        expected_unconditional_event = EditUserForwardEvent(self.user.uuid,
                                                            'unconditional',
                                                            self.user.unconditional_enabled,
                                                            self.user.unconditional_destination)
        expected_calls = [call(expected_busy_event,
                               expected_busy_event.routing_key,
                               headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True}),
                          call(expected_noanswer_event,
                               expected_noanswer_event.routing_key,
                               headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True}),
                          call(expected_unconditional_event,
                               expected_unconditional_event.routing_key,
                               headers={'user_uuid:{uuid}'.format(uuid=self.user.uuid): True})]
        self.bus.send_bus_event.assert_has_calls(expected_calls)
