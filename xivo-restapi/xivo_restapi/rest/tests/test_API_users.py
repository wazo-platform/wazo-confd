# -*- coding: UTF-8 -*-

# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from mock import Mock
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi.rest import rest_encoder
from xivo_restapi.rest.helpers import users_helper
from xivo_restapi.rest.tests import instance_user_management
from xivo_restapi.restapi_config import RestAPIConfig
import unittest
from xivo_restapi.services.utils.exceptions import NoSuchElementException


class TestAPIUsers(unittest.TestCase):

    def setUp(self):
        self.instance_user_management = instance_user_management
        from xivo_restapi.rest import flask_http_server
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    def test_list_users(self):
        status = "200 OK"
        user1 = UserFeatures()
        user1.firstname = 'test1'
        user2 = UserFeatures()
        user2.firstname = 'test2'
        expected_list = [user1, user2]
        expected_result = {"items": expected_list}
        self.instance_user_management.get_all_users.return_value = expected_list
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              '')

        self.instance_user_management.get_all_users.assert_any_call()
        self.assertEquals(result.status, status)
        self.assertEquals(rest_encoder.encode(expected_result), result.data)

    def test_list_users_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_all_users():
            raise Exception()

        self.instance_user_management.get_all_users\
                    .side_effect = mock_get_all_users
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/')

        self.instance_user_management.get_all_users.assert_any_call()
        self.assertEqual(result.status, status)
        self.instance_user_management.get_all_users.side_effect = None

    def test_get(self):
        status = "200 OK"
        user1 = UserFeatures()
        user1.firstname = 'test1'
        self.instance_user_management.get_user.return_value = user1
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              '')

        self.instance_user_management.get_user.assert_called_with(1)
        self.assertEquals(result.status, status)
        self.assertEquals(rest_encoder.encode(user1), result.data)

    def test_get_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_get_user():
            raise Exception()

        self.instance_user_management.get_user.side_effect = mock_get_user
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')

        self.instance_user_management.get_user.assert_called_with(1)
        self.assertEqual(result.status, status)
        self.instance_user_management.get_user.side_effect = None

    def test_get_not_found(self):
        status = "404 NOT FOUND"

        def mock_get_user(userid):
            raise NoSuchElementException("No such user")

        self.instance_user_management.get_user.side_effect = mock_get_user
        result = self.app.get(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')

        self.instance_user_management.get_user.assert_called_with(1)
        self.assertEqual(result.status, status)
        self.instance_user_management.get_user.side_effect = None

    def test_create(self):
        status = "201 CREATED"
        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        self.instance_user_management.create_user.return_value = True
        user = UserFeatures()
        users_helper.create_instance = Mock()
        users_helper.create_instance.return_value = user
        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              data=rest_encoder.encode(data))
        self.assertEqual(result.status, status)
        users_helper.create_instance.assert_called_with(data)
        self.instance_user_management.create_user.assert_called_with(user)

    def test_create_error(self):
        status = "500 INTERNAL SERVER ERROR"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        def mock_create_user(user):
            raise Exception()

        self.instance_user_management.create_user.side_effect = mock_create_user
        result = self.app.post(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/',
                              data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_user_management.create_user.side_effect = None

    def test_edit(self):
        status = "200 OK"
        data = {u'id': 2,
                u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        self.instance_user_management.edit_user.return_value = True
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.assertEqual(result.status, status)
        self.instance_user_management.edit_user.assert_called_with(1, data)

    def test_edit_error(self):
        status = "500 INTERNAL SERVER ERROR"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        def mock_edit_user(userid, data):
            raise Exception()

        self.instance_user_management.edit_user.side_effect = mock_edit_user
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_user_management.edit_user.side_effect = None

    def test_edit_not_found(self):
        status = "404 NOT FOUND"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        def mock_edit_user(userid, data):
            raise NoSuchElementException('')

        self.instance_user_management.edit_user.side_effect = mock_edit_user
        result = self.app.put(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                              RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1',
                              data=rest_encoder.encode(data))
        self.assertEqual(status, result.status)
        self.instance_user_management.edit_user.side_effect = None

    def test_delete(self):
        status = "200 OK"
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                                 RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.assertEqual(result.status, status)
        self.instance_user_management.delete_user.assert_called_with(1)

    def test_delete_not_error(self):
        status = "500 INTERNAL SERVER ERROR"

        def mock_delete_user(userid):
            raise Exception
        self.instance_user_management.delete_user.side_effect = mock_delete_user
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                                 RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.assertEqual(result.status, status)
        self.instance_user_management.delete_user.assert_called_with(1)

    def test_delete_not_found(self):
        status = "404 NOT FOUND"

        def mock_delete_user(userid):
            raise NoSuchElementException('')
        self.instance_user_management.delete_user.side_effect = mock_delete_user
        result = self.app.delete(RestAPIConfig.XIVO_REST_SERVICE_ROOT_PATH +
                                 RestAPIConfig.XIVO_USERS_SERVICE_PATH + '/1')
        self.assertEqual(result.status, status)
        self.instance_user_management.delete_user.assert_called_with(1)
