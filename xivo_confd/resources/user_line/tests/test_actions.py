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

import unittest
from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_confd.resources.user_line.actions import UserLineService


class TestUserLineService(unittest.TestCase):

    def setUp(self):
        self.old_service = Mock()
        self.user_dao = Mock()
        self.line_dao = Mock()
        self.service = UserLineService(self.old_service, self.user_dao, self.line_dao)

    def test_when_listing_associations_then_user_is_checked(self):
        self.service.list(sentinel.user_id)

        self.user_dao.get.assert_called_once_with(sentinel.user_id)

    def test_when_listing_associations_then_service_is_called(self):
        expected_user_lines = self.old_service.find_all_by_user_id.return_value

        result = self.service.list(sentinel.user_id)

        self.old_service.find_all_by_user_id.assert_called_once_with(sentinel.user_id)
        assert_that(result, equal_to(expected_user_lines))

    def test_when_getting_association_then_service_is_called(self):
        expected_user_line = self.old_service.get_by_user_id_and_line_id.return_value

        result = self.service.get(sentinel.user_id, sentinel.line_id)

        self.old_service.get_by_user_id_and_line_id.assert_called_once_with(sentinel.user_id,
                                                                            sentinel.line_id)
        assert_that(result, equal_to(expected_user_line))

    def test_when_associating_then_user_is_checked(self):
        association = Mock(user_id=sentinel.user_id)
        self.service.associate(association)

        self.user_dao.get.assert_called_once_with(sentinel.user_id)

    def test_when_associating_then_line_is_checked(self):
        association = Mock(line_id=sentinel.line_id)
        self.service.associate(association)

        self.line_dao.get.assert_called_once_with(sentinel.line_id)

    def test_when_associating_then_service_is_called(self):
        association = Mock()
        self.service.associate(association)

        self.old_service.associate.assert_called_once_with(association)

    def test_when_dissociating_then_user_is_checked(self):
        association = Mock(user_id=sentinel.user_id)
        self.service.dissociate(association)

        self.user_dao.get.assert_called_once_with(sentinel.user_id)

    def test_when_dissociating_then_line_is_checked(self):
        association = Mock(line_id=sentinel.line_id)
        self.service.dissociate(association)

        self.line_dao.get.assert_called_once_with(sentinel.line_id)

    def test_when_dissociating_then_service_is_called(self):
        association = Mock()
        self.service.dissociate(association)

        self.old_service.dissociate.assert_called_once_with(association)
