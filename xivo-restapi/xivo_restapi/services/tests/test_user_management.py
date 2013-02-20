'''
Created on Feb 20, 2013

@author: jean
'''
from mock import Mock
from xivo_dao import user_dao
from xivo_restapi.services.user_management import UserManagement
import unittest
from xivo_dao.alchemy.userfeatures import UserFeatures


class TestUserManagement(unittest.TestCase):

    def setUp(self):
        self._userManager = UserManagement()

    def test_get_all_users(self):
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user2 = UserFeatures()
        user2.firstname = 'test2'
        user_dao.get_all = Mock()
        user_dao.get_all.return_value = [user1, user2]
        result = self._userManager.get_all_users()
        user_dao.get_all.assert_any_call()
        self.assertEqual(result, [user1, user2])

    def test_get_user(self):
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user_dao.get = Mock()
        user_dao.get.return_value = user1
        result = self._userManager.get_user(1)
        user_dao.get.assert_called_with(1)
        self.assertEqual(result, user1)
