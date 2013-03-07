'''
Created on Feb 20, 2013

@author: jean
'''
from mock import Mock
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.rest.helpers import global_helper
from xivo_restapi.rest.helpers.users_helper import UsersHelper
from xivo_restapi.services.utils.exceptions import IncorrectParametersException
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
