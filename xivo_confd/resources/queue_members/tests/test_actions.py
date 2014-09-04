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

from xivo_dao.data_handler.queue_members.model import QueueMemberAgent
from xivo_confd.helpers.tests.test_resources import TestResources


BASE_URL = '/1.1/queues/%s/members/agents'
EDIT_URL = BASE_URL + '/%s'


class TestQueueMemberActions(TestResources):

    def setUp(self):
        super(TestQueueMemberActions, self).setUp()
        self.queue_member = QueueMemberAgent(agent_id=12, queue_id=3, penalty=5)

    @patch('xivo_dao.data_handler.queue_members.services.get_by_queue_id_and_agent_id')
    def test_get_agent_queue_association(self, get_by_queue_id_and_agent_id):
        get_by_queue_id_and_agent_id.return_value = self.queue_member

        expected_result = {
            u'agent_id': self.queue_member.agent_id,
            u'queue_id': self.queue_member.queue_id,
            u'penalty': self.queue_member.penalty
        }

        result = self.app.get(EDIT_URL % (self.queue_member.queue_id, self.queue_member.agent_id))

        self.assert_response_for_list(result, expected_result)
        get_by_queue_id_and_agent_id.assert_called_once_with(self.queue_member.queue_id, self.queue_member.agent_id)

    @patch('xivo_dao.data_handler.queue_members.services.get_by_queue_id_and_agent_id')
    @patch('xivo_dao.data_handler.queue_members.services.edit_agent_queue_association')
    def test_edit_agent_queue_association(self, edit_agent_queue_association, get_by_queue_id_and_agent_id):
        get_by_queue_id_and_agent_id.return_value = self.queue_member

        data = {'penalty': self.queue_member.penalty}
        data_serialized = self._serialize_encode(data)
        result = self.app.put(EDIT_URL % (self.queue_member.queue_id, self.queue_member.agent_id), data=data_serialized)

        self.assert_response_for_update(result)
        get_by_queue_id_and_agent_id.assert_called_once_with(self.queue_member.queue_id, self.queue_member.agent_id)
        edit_agent_queue_association.assert_called_once_with(self.queue_member)

    @patch('xivo_dao.data_handler.queue_members.services.associate_agent_to_queue')
    def test_associate_agent_to_queue(self,associate_agent_to_queue):
        associate_agent_to_queue.return_value = self.queue_member

        expected_result = {
            u'agent_id': self.queue_member.agent_id,
            u'queue_id': self.queue_member.queue_id,
            u'penalty': self.queue_member.penalty
        }

        data = {'agent_id': self.queue_member.agent_id, 'penalty': self.queue_member.penalty}
        data_serialized = self._serialize_encode(data)
        result = self.app.post(BASE_URL % (self.queue_member.queue_id), data=data_serialized)
        self.assert_response_for_create(result,expected_result)

        location = result.headers['location']

        assert_that(location,equal_to('http://localhost/1.1/queues/3/members/agents/12'))
        associate_agent_to_queue.assert_called_once_with(self.queue_member)
