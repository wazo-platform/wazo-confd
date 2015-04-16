# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>
from mock import patch
import unittest

from xivo_dao.resources.queue_members import validator
from xivo_dao.resources.queue_members.model import QueueMemberAgent
from xivo_dao.resources.exception import NotFoundError, ResourceError
from xivo_dao.resources.exception import InputError


class TestQueueMembersValidator(unittest.TestCase):
    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                   patch_get_agent):
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        validator.validate_edit_agent_queue_association(queue_member)

        patch_get_queue.assert_called_once_with(queue_member.queue_id)
        patch_get_by_queue_and_agent.assert_called_once_with(queue_member.queue_id, queue_member.agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_queue(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                                 patch_get_agent):
        patch_get_queue.side_effect = LookupError
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(NotFoundError, validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_association(self, patch_get_by_queue_and_agent,
                                                                       patch_get_queue, patch_get_agent):
        patch_get_by_queue_and_agent.side_effect = NotFoundError
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(NotFoundError, validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_agent(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                                 patch_get_agent):
        patch_get_agent.return_value = None
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(NotFoundError, validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_get_agent_queue_association(self, patch_get_queue, patch_get_agent):
        queue_id = 5
        agent_id = 3
        validator.validate_get_agent_queue_association(queue_id, agent_id)

        patch_get_queue.assert_called_once_with(queue_id)
        patch_get_agent.assert_called_once_with(agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_get_agent_queue_association_no_such_queue(self, patch_get_queue, patch_get_agent):
        queue_id = 5
        agent_id = 3
        patch_get_queue.side_effect = LookupError

        self.assertRaises(NotFoundError, validator.validate_get_agent_queue_association, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_get_agent_queue_association_no_such_agent(self, patch_get_queue, patch_get_agent):
        queue_id = 5
        agent_id = 3
        patch_get_agent.return_value = None

        self.assertRaises(NotFoundError, validator.validate_get_agent_queue_association, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_associate_agent_queue_no_such_queue(self, patch_get_queue, patch_get_agent):
        queue_id = 5
        agent_id = 3
        patch_get_queue.side_effect = LookupError

        self.assertRaises(NotFoundError, validator.validate_associate_agent_queue, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_associate_agent_queue_no_such_agent(self, patch_get_queue, patch_get_agent):
        queue_id = 5
        agent_id = 3
        patch_get_agent.return_value = None

        self.assertRaises(InputError, validator.validate_associate_agent_queue, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_associate_agent_queue_already_exists(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                           patch_get_agent):
        queue_id = 8
        agent_id = 9
        queue_member = QueueMemberAgent
        patch_get_by_queue_and_agent.return_value = queue_member

        self.assertRaises(ResourceError, validator.validate_associate_agent_queue, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_remove_agent_from_queue_no_such_queue(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                            patch_get_agent):
        patch_get_queue.side_effect = LookupError

        self.assertRaises(NotFoundError, validator.validate_remove_agent_from_queue, agent_id=3, queue_id=5)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_remove_agent_from_queue_no_such_agent(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                            patch_get_agent):
        patch_get_agent.return_value = None

        self.assertRaises(NotFoundError, validator.validate_remove_agent_from_queue, agent_id=3, queue_id=5)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_remove_agent_from_queue_no_such_association(self, patch_get_by_queue_and_agent, patch_get_queue,
                                                                  patch_get_agent):
        patch_get_by_queue_and_agent.side_effect = NotFoundError

        self.assertRaises(NotFoundError, validator.validate_remove_agent_from_queue, agent_id=3, queue_id=5)
