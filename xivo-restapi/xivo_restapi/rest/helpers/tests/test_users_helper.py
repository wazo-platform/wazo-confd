'''
Created on Feb 20, 2013

@author: jean
'''
from mock import Mock
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.rest.helpers import global_helper, users_helper
import unittest


class TestUsersHelper(unittest.TestCase):

    def test_create_instance(self):
        data = {'firstname': 'name'}
        global_helper.create_class_instance = Mock()
        mock_return_value = Mock()
        global_helper.create_class_instance.return_value = mock_return_value
        result = users_helper.create_instance(data)
        global_helper.create_class_instance.assert_called_with(UserFeatures, data)
        self.assertEqual(result, mock_return_value)
