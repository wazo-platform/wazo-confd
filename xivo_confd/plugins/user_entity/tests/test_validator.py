# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
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

from xivo_confd.plugins.user_entity.validator import UserEntityAssociationValidator

from xivo_dao.helpers.exception import ResourceError


class TestValidateNoLineAssociated(unittest.TestCase):

    def setUp(self):
        self.dao = Mock()
        self.validator = UserEntityAssociationValidator(self.dao)

    def test_given_line_associated_then_validation_fails(self):
        user = Mock(id=sentinel.id)
        self.dao.find_all_by.return_value = [Mock(line_id=sentinel.line_id)]

        self.assertRaises(ResourceError, self.validator.validate_user_no_line_associated, user)

        self.dao.find_all_by.assert_called_once_with(user_id=user.id)

    def test_given_no_line_associated_then_validation_passes(self):
        user = Mock(id=sentinel.id)
        self.dao.find_all_by.return_value = []

        self.validator.validate_user_no_line_associated(user)

        self.dao.find_all_by.assert_called_once_with(user_id=user.id)
