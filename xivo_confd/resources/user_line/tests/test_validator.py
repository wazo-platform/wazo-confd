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

from mock import patch, Mock
import unittest

from xivo_dao.resources.exception import InputError
from xivo_dao.resources.exception import ResourceError
from xivo_dao.resources.exception import NotFoundError
from xivo_dao.resources.user_line import validator
from xivo_dao.resources.user_line.model import UserLine


class TestValidator(unittest.TestCase):

    def test_validate_association_missing_parameters(self):
        user_line = UserLine()

        self.assertRaises(InputError, validator.validate_association, user_line)

    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_association_when_user_does_not_exist(self, user_get):
        user_line = UserLine(user_id=1, line_id=2)

        user_get.side_effect = NotFoundError
        self.assertRaises(InputError, validator.validate_association, user_line)
        user_get.assert_called_once_with(user_line.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.line.dao.get')
    def test_validate_association_when_line_does_not_exist(self, line_get, user_get):
        user_line = UserLine(user_id=1, line_id=2)

        line_get.side_effect = NotFoundError
        self.assertRaises(InputError, validator.validate_association, user_line)
        line_get.assert_called_once_with(user_line.line_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_validate_association_when_user_already_has_a_line(self,
                                                               user_line_find_all_by_user_id,
                                                               line_get,
                                                               user_get):
        user_line = UserLine(user_id=1, line_id=2)

        user_line_find_all_by_user_id.return_value = [user_line]

        self.assertRaises(ResourceError, validator.validate_association, user_line)
        user_line_find_all_by_user_id.assert_called_once_with(user_line.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_validate_association_when_user_has_a_different_line(self,
                                                                 user_line_find_all_by_user_id,
                                                                 line_get,
                                                                 user_get):
        user_line = UserLine(user_id=1, line_id=2)
        existing_user_line = UserLine(user_id=1, line_id=3)

        user_line_find_all_by_user_id.return_value = [existing_user_line]

        self.assertRaises(ResourceError, validator.validate_association, user_line)
        user_line_find_all_by_user_id.assert_called_once_with(user_line.user_id)

    @patch('xivo_dao.resources.user.dao.get')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    def test_validate_association(self,
                                  user_line_find_all_by_user_id,
                                  line_get,
                                  user_get):
        user_line = UserLine(user_id=1, line_id=2)

        user_line_find_all_by_user_id.return_value = []

        validator.validate_association(user_line)
        user_get.assert_called_once_with(user_line.user_id)
        line_get.assert_called_once_with(user_line.line_id)
        user_line_find_all_by_user_id.assert_called_once_with(user_line.user_id)

    @patch('xivo_dao.resources.user_line.dao.line_has_secondary_user')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation_user_not_exists(self,
                                                   user_dao_get,
                                                   line_dao_get,
                                                   user_line_dao_find_all_by_user_id,
                                                   line_has_secondary_user):
        user_line = Mock(UserLine, user_id=3)

        user_dao_get.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_dissociation, user_line)
        user_dao_get.assert_called_once_with(user_line.user_id)
        self.assertEquals(line_dao_get.call_count, 0)
        self.assertEquals(user_line_dao_find_all_by_user_id.call_count, 0)
        self.assertEquals(line_has_secondary_user.call_count, 0)

    @patch('xivo_dao.resources.user_line.dao.line_has_secondary_user')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation_no_line(self,
                                           user_dao_get,
                                           line_dao_get,
                                           user_line_dao_find_all_by_user_id,
                                           line_has_secondary_user):
        user_line = Mock(UserLine, user_id=3, line_id=4)

        user_dao_get.return_value = Mock()
        line_dao_get.side_effect = NotFoundError

        self.assertRaises(InputError, validator.validate_dissociation, user_line)
        user_dao_get.assert_called_once_with(user_line.user_id)
        line_dao_get.assert_called_once_with(user_line.line_id)
        self.assertEquals(user_line_dao_find_all_by_user_id.call_count, 0)
        self.assertEquals(line_has_secondary_user.call_count, 0)

    @patch('xivo_dao.resources.line_device.validator.validate_no_device')
    @patch('xivo_dao.resources.user_line.dao.line_has_secondary_user')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation(self,
                                   user_dao_get,
                                   line_dao_get,
                                   user_line_dao_find_all_by_user_id,
                                   line_has_secondary_user,
                                   validate_no_device):
        user_line = UserLine(user_id=3,
                             line_id=4,
                             main_user=True)

        user_line_dao_find_all_by_user_id.return_value = [user_line]
        line_has_secondary_user.return_value = False

        validator.validate_dissociation(user_line)
        user_dao_get.assert_called_once_with(user_line.user_id)
        line_dao_get.assert_called_once_with(user_line.line_id)
        user_line_dao_find_all_by_user_id.assert_called_once_with(user_line.user_id)
        line_has_secondary_user.assert_called_once_with(user_line)
        validate_no_device.assert_called_once_with(user_line.line_id)

    @patch('xivo_dao.resources.user_line.dao.line_has_secondary_user')
    @patch('xivo_dao.resources.user_line.dao.find_all_by_user_id')
    @patch('xivo_dao.resources.line.dao.get')
    @patch('xivo_dao.resources.user.dao.get')
    def test_validate_dissociation_main_user_with_secondary_user(self,
                                                                 user_dao_get,
                                                                 line_dao_get,
                                                                 user_line_dao_find_all_by_user_id,
                                                                 line_has_secondary_user):
        user_line = UserLine(user_id=3,
                             line_id=4,
                             main_user=True)

        user_line_dao_find_all_by_user_id.return_value = [user_line]
        line_has_secondary_user.return_value = True

        self.assertRaises(ResourceError, validator.validate_dissociation, user_line)
        user_dao_get.assert_called_once_with(user_line.user_id)
        line_dao_get.assert_called_once_with(user_line.line_id)
        user_line_dao_find_all_by_user_id.assert_called_once_with(user_line.user_id)
        line_has_secondary_user.assert_called_once_with(user_line)
