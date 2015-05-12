# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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
import unittest

from hamcrest import assert_that, equal_to
from mock import Mock

from xivo_dao.resources.queue_members.model import QueueMemberAgent

from xivo_confd.resources.queue_members.actions import QueueMemberService


class TestQueueMembers(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = Mock()
        self.notifier = Mock()
        self.service = QueueMemberService(self.dao, self.validator, self.notifier)

    def test_get_by_queue_id_and_agent_id(self):
        agent_id = 3
        queue_id = 2
        queue_member = self.dao.get_by_queue_id_and_agent_id.return_value = QueueMemberAgent(agent_id=agent_id,
                                                                                             queue_id=queue_id, penalty=5)

        result = self.service.get(queue_id, agent_id)

        self.validator.validate_get_agent_queue_association.assert_called_once_with(queue_id, agent_id)
        self.dao.get_by_queue_id_and_agent_id.assert_called_once_with(queue_id, agent_id)
        assert_that(result, equal_to(queue_member))

    def test_edit_agent_queue_association(self):
        queue_member = QueueMemberAgent(agent_id=12, queue_id=2, penalty=4)

        self.service.edit(queue_member)

        self.validator.validate_edit_agent_queue_association.assert_called_once_with(queue_member)
        self.dao.edit_agent_queue_association.assert_called_once_with(queue_member)
        self.notifier.agent_queue_association_updated.assert_called_once_with(queue_member)

    def test_associate_agent_to_queue(self):
        queue_member = QueueMemberAgent(agent_id=31, queue_id=7, penalty=3)
        self.dao.associate.return_value = queue_member

        qm = self.service.associate(queue_member)

        self.validator.validate_associate_agent_queue.assert_called_once_with(queue_member.queue_id, queue_member.agent_id)
        self.dao.associate.assert_called_once_with(queue_member)
        self.notifier.agent_queue_associated.assert_called_once_with(queue_member)
        assert_that(qm, equal_to(queue_member))

    def test_remove_agent_from_queue(self):
        queue_member = QueueMemberAgent(agent_id=31, queue_id=7)

        self.service.dissociate(queue_member)

        self.validator.validate_remove_agent_from_queue.assert_called_once_with(queue_member.agent_id, queue_member.queue_id)
        self.dao.remove_agent_from_queue.assert_called_once_with(queue_member.agent_id, queue_member.queue_id)
        self.notifier.agent_removed_from_queue.assert_called_once_with(queue_member.agent_id, queue_member.queue_id)
