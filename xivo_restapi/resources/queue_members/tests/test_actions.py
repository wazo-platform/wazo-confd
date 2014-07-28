# -*- coding: utf-8 -*-
#
# Copyright (C) 2013 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import assert_that, equal_to
from mock import patch

from xivo_dao.data_handler.queue_members.exception import QueueNotExistsError, \
    QueueMemberNotExistsError
from xivo_dao.data_handler.queue_members.model import QueueMember
from xivo_restapi.helpers.tests.test_resources import TestResources


BASE_URL = '/1.1/queues/%s/memberships/agents/%s'


class TestQueueMemberActions(TestResources):

    def setUp(self):
        super(TestQueueMemberActions, self).setUp()
        self.queue_member = QueueMember(agent_id=12, queue_id=3, penalty=5)

    @patch('xivo_dao.data_handler.queue_members.services.get_by_queue_id_and_agent_id')
    def test_get_agent_queue_association(self, get_by_queue_id_and_agent_id):
        get_by_queue_id_and_agent_id.return_value = self.queue_member

        expected_result = {
            u'agent_id': self.queue_member.agent_id,
            u'queue_id': self.queue_member.queue_id,
            u'penalty': self.queue_member.penalty
        }

        result = self.app.get(BASE_URL % (self.queue_member.queue_id, self.queue_member.agent_id))
        self.assert_response_for_list(result, expected_result)

    @patch('xivo_dao.data_handler.queue_members.services.get_by_queue_id_and_agent_id')
    def test_get_agent_queue_association_no_such_queue(self, get_by_queue_id_and_agent_id):
        get_by_queue_id_and_agent_id.side_effect = QueueNotExistsError('Queue', id=self.queue_member.queue_id)
        expected_result = ['Queue with id=%s does not exist' % self.queue_member.queue_id]

        result = self.app.get(BASE_URL % (self.queue_member.queue_id, self.queue_member.agent_id))
        assert_that(result.status_code, equal_to(404))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.queue_members.services.get_by_queue_id_and_agent_id')
    def test_get_agent_queue_association_no_such_member(self, get_by_queue_id_and_agent_id):
        get_by_queue_id_and_agent_id.side_effect = QueueMemberNotExistsError('QueueMember', queue_id=self.queue_member.queue_id,
                                                                                            agent_id=self.queue_member.agent_id)
        expected_result = ['QueueMember with agent_id=%s queue_id=%s does not exist' % (self.queue_member.agent_id, self.queue_member.queue_id)]

        result = self.app.get(BASE_URL % (self.queue_member.queue_id, self.queue_member.agent_id))
        assert_that(result.status_code, equal_to(404))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.queue_members.services.edit_agent_queue_association')
    def test_edit_agent_queue_association(self, edit_agent_queue_association):
        data = {'penalty': self.queue_member.penalty}
        data_serialized = self._serialize_encode(data)

        result = self.app.put(BASE_URL % (self.queue_member.queue_id, self.queue_member.agent_id), data=data_serialized)
        assert_that(result.status_code, equal_to(204))

    @patch('xivo_dao.data_handler.queue_members.services.edit_agent_queue_association')
    def test_edit_agent_queue_association_no_such_queue(self, edit_agent_queue_association):
        edit_agent_queue_association.side_effect = QueueNotExistsError('Queue', id=self.queue_member.queue_id)
        expected_result = ['Queue with id=%s does not exist' % self.queue_member.queue_id]
        data = {'penalty': self.queue_member.penalty}
        data_serialized = self._serialize_encode(data)

        result = self.app.put(BASE_URL % (self.queue_member.queue_id, self.queue_member.agent_id), data=data_serialized)
        assert_that(result.status_code, equal_to(404))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.queue_members.services.edit_agent_queue_association')
    def test_edit_agent_queue_association_no_such_member(self, edit_agent_queue_association):
        edit_agent_queue_association.side_effect = QueueMemberNotExistsError('QueueMember', queue_id=self.queue_member.queue_id,
                                                                                            agent_id=self.queue_member.agent_id)
        expected_result = ['QueueMember with agent_id=%s queue_id=%s does not exist' % (self.queue_member.agent_id, self.queue_member.queue_id)]

        data = {'penalty': self.queue_member.penalty}
        data_serialized = self._serialize_encode(data)

        result = self.app.put(BASE_URL % (self.queue_member.queue_id, self.queue_member.agent_id), data=data_serialized)
        assert_that(result.status_code, equal_to(404))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))
