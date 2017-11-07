# -*- coding: utf-8 -*-

# Copyright (C) 2013-2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

import unittest

from mock import patch

from xivo_dao.helpers.exception import NotFoundError, ResourceError
from xivo_dao.helpers.exception import InputError
from xivo_dao.resources.queue_members.model import QueueMemberAgent

from xivo_confd.plugins.queue_member.validator import QueueMemberAssociationValidator


class TestQueueMembersValidator(unittest.TestCase):

    def setUp(self):
        self.validator = QueueMemberAssociationValidator()

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association(self, patch_get_by_queue_and_agent, patch_get_queue, _):
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.validator.validate_edit_agent_queue_association(queue_member)

        patch_get_queue.assert_called_once_with(queue_member.queue_id)
        patch_get_by_queue_and_agent.assert_called_once_with(queue_member.queue_id, queue_member.agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_queue(self, _, patch_get_queue, __):
        patch_get_queue.side_effect = LookupError
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(NotFoundError, self.validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_association(self, patch_get_by_queue_and_agent, _, __):
        patch_get_by_queue_and_agent.side_effect = NotFoundError
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(NotFoundError, self.validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_edit_agent_queue_association_no_such_agent(self, _, __, patch_get_agent):
        patch_get_agent.return_value = None
        queue_member = QueueMemberAgent(agent_id=3, queue_id=5, penalty=3)
        self.assertRaises(NotFoundError, self.validator.validate_edit_agent_queue_association, queue_member)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_get_agent_queue_association(self, patch_get_queue, patch_get_agent):
        queue_id = 5
        agent_id = 3
        self.validator.validate_get_agent_queue_association(queue_id, agent_id)

        patch_get_queue.assert_called_once_with(queue_id)
        patch_get_agent.assert_called_once_with(agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_get_agent_queue_association_no_such_queue(self, patch_get_queue, _):
        queue_id = 5
        agent_id = 3
        patch_get_queue.side_effect = LookupError

        self.assertRaises(NotFoundError, self.validator.validate_get_agent_queue_association, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_get_agent_queue_association_no_such_agent(self, _, patch_get_agent):
        queue_id = 5
        agent_id = 3
        patch_get_agent.return_value = None

        self.assertRaises(NotFoundError, self.validator.validate_get_agent_queue_association, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_associate_agent_queue_no_such_queue(self, patch_get_queue, _):
        queue_id = 5
        agent_id = 3
        patch_get_queue.side_effect = LookupError

        self.assertRaises(NotFoundError, self.validator.validate_associate_agent_queue, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    def test_validate_associate_agent_queue_no_such_agent(self, _, patch_get_agent):
        queue_id = 5
        agent_id = 3
        patch_get_agent.return_value = None

        self.assertRaises(InputError, self.validator.validate_associate_agent_queue, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_associate_agent_queue_already_exists(self, patch_get_by_queue_and_agent, _, __):
        queue_id = 8
        agent_id = 9
        queue_member = QueueMemberAgent
        patch_get_by_queue_and_agent.return_value = queue_member

        self.assertRaises(ResourceError, self.validator.validate_associate_agent_queue, queue_id, agent_id)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_remove_agent_from_queue_no_such_queue(self, _, patch_get_queue, __):
        patch_get_queue.side_effect = LookupError

        self.assertRaises(NotFoundError, self.validator.validate_remove_agent_from_queue, agent_id=3, queue_id=5)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_remove_agent_from_queue_no_such_agent(self, _, __, patch_get_agent):
        patch_get_agent.return_value = None

        self.assertRaises(NotFoundError, self.validator.validate_remove_agent_from_queue, agent_id=3, queue_id=5)

    @patch('xivo_dao.agent_dao.get')
    @patch('xivo_dao.queue_dao.get')
    @patch('xivo_dao.resources.queue_members.dao.get_by_queue_id_and_agent_id')
    def test_validate_remove_agent_from_queue_no_such_association(self, patch_get_by_queue_and_agent, _, __):
        patch_get_by_queue_and_agent.side_effect = NotFoundError

        self.assertRaises(NotFoundError, self.validator.validate_remove_agent_from_queue, agent_id=3, queue_id=5)
