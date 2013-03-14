# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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
from mock import Mock
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.rest.helpers import global_helper
from xivo_restapi.rest.helpers.users_helper import UsersHelper
from xivo_dao.service_data_model.sdm_exception import IncorrectParametersException
import unittest


class TestUsersHelper(unittest.TestCase):

    def setUp(self):
        self.users_helper = UsersHelper()

    def test_create_instance_success(self):
        data = {'firstname': 'name'}
        global_helper.create_class_instance = Mock()
        mock_return_value = Mock()
        global_helper.create_class_instance.return_value = mock_return_value
        result = self.users_helper.create_instance(data)
        global_helper.create_class_instance.assert_called_with(UserFeatures, data) #@UndefinedVariable
        self.assertEqual(result, mock_return_value)

    def test_create_instance_fail(self):
        data = {"unexisting_field": "value"}
        got_exception = False
        try:
            self.users_helper.create_instance(data)
        except IncorrectParametersException as e:
            got_exception = True
            self.assertEquals(str(e), "Incorrect parameters sent: unexisting_field")
        self.assertTrue(got_exception)

    def test_validate_data_success(self):
        data = {'firstname': 'name'}
        try:
            self.users_helper.validate_data(data)
        except:
            self.assertTrue(False, "An unexpected exception occured")
        self.assertTrue(True)

    def test_validate_data_fail(self):
        data = {"unexisting_field": "value"}
        self.assertRaises(IncorrectParametersException, self.users_helper.validate_data, data)
