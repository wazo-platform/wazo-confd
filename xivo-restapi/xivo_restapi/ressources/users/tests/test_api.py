# -*- coding: UTF-8 -*-

# Copyright (C) 2013 Avencall
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

import unittest

from mock import Mock, patch
from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_restapi import flask_http_server
from xivo_restapi.ressources.users.mapper import UserMapper
from xivo_restapi.helpers import serializer
from xivo_dao.data_handler.user.model import User
from xivo_dao.helpers.services_exception import MissingParametersError

BASE_URL = "/1.1/users"


class TestAPIUsers(unittest.TestCase):

    def setUp(self):
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users(self, mock_user_services_find_all):
        status = "200 OK"
        user1 = UserFeatures()
        user1.id = 1
        user1.firstname = 'test1'
        user1 = User.from_data_source(user1)
        user2 = UserFeatures()
        user2.id = 2
        user2.firstname = 'test2'
        user2 = User.from_data_source(user2)
        expected_list = [user1, user2]

        mock_user_services_find_all.return_value = expected_list

        expected_result = {
            "total": len(expected_list),
            "items": UserMapper.run_list_object(expected_list)
        }

        result = self.app.get("%s/" % BASE_URL, '')

        mock_user_services_find_all.assert_any_call()
        self.assertEquals(result.status, status)
        self.assertEquals(serializer.encode(expected_result), result.data)

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_error(self, mock_user_services_find_all):
        status = "500 INTERNAL SERVER ERROR"
        mock_user_services_find_all.side_effect = Exception

        result = self.app.get("%s/" % BASE_URL)

        mock_user_services_find_all.assert_any_call()
        self.assertEqual(result.status, status)
        mock_user_services_find_all.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    def test_get(self, mock_user_services_get_by_user_id):
        status = "200 OK"
        user1 = UserFeatures()
        user1.id = 1
        user1.firstname = 'test1'
        user1 = User.from_data_source(user1)
        mock_user_services_get_by_user_id.return_value = user1
        user1 = UserMapper.run_one_object(user1)

        result = self.app.get("%s/1" % BASE_URL, '')

        mock_user_services_get_by_user_id.assert_called_with(1)
        self.assertEquals(result.status, status)
        self.assertEquals(serializer.encode(user1), result.data)

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    def test_get_error(self, mock_user_services_get_by_user_id):
        status = "500 INTERNAL SERVER ERROR"
        mock_user_services_get_by_user_id.side_effect = Exception

        result = self.app.get("%s/1" % BASE_URL)

        mock_user_services_get_by_user_id.assert_called_with(1)
        self.assertEqual(result.status, status)
        mock_user_services_get_by_user_id.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    def test_get_not_found(self, mock_user_services_get_by_user_id):
        status = "404 NOT FOUND"

        mock_user_services_get_by_user_id.side_effect = LookupError("No such user")

        result = self.app.get("%s/1" % BASE_URL)

        mock_user_services_get_by_user_id.assert_called_with(1)
        self.assertEqual(result.status, status)
        mock_user_services_get_by_user_id.side_effect = None

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create(self, mock_user_services_create):
        status = "201 CREATED"
        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        mock_user_services_create.return_value = 1

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(result.status, status)
        self.assertEqual(result.data, '1')
        mock_user_services_create.assert_called_with(User.from_user_data(data))

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create_error(self, mock_user_services_create):
        status = "500 INTERNAL SERVER ERROR"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        mock_user_services_create.side_effect = Exception

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status, result.status)
        mock_user_services_create.side_effect = None

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create_request_error(self, mock_user_services_create):
        status = "400 BAD REQUEST"
        expected_data = "Missing parameters: lastname"
        data = {'firstname': 'André'}
        mock_user_services_create.side_effect = MissingParametersError(["lastname"])

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status, result.status)
        received_data = serializer.decode(result.data)
        self.assertEquals(expected_data, received_data[0])
        mock_user_services_create.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit(self, mock_user_services_edit, mock_user_services_get_by_user_id):
        status = "200 OK"
        data = {u'id': 1,
                u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        mock_user_services_get_by_user_id.return_value = Mock(User)

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(result.status, status)
        mock_user_services_edit.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit_error(self, mock_user_services_edit, mock_user_services_get_by_user_id):
        status = "500 INTERNAL SERVER ERROR"
        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}
        mock_user_services_get_by_user_id.return_value = user = Mock(User)
        mock_user_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        user.update_from_data.assert_called_with(data)
        self.assertEqual(status, result.status)
        mock_user_services_edit.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit_not_found(self, mock_user_services_edit, mock_user_services_get_by_user_id):
        status = "404 NOT FOUND"
        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}
        mock_user_services_get_by_user_id.return_value = Mock(User)

        mock_user_services_edit.side_effect = LookupError('')

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status, result.status)
        mock_user_services_edit.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_success(self, mock_user_services_delete, mock_user_services_get_by_user_id):
        status = "200 OK"
        user = Mock(User)
        mock_user_services_get_by_user_id.return_value = user
        mock_user_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(result.status, status)
        mock_user_services_delete.assert_called_with(user)
        mock_user_services_delete.side_effect = None

    @patch('xivo_dao.data_handler.user.services.get_by_user_id')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_not_found(self, mock_user_services_delete, mock_user_services_get_by_user_id):
        status = "404 NOT FOUND"
        user = Mock(User)
        mock_user_services_get_by_user_id.return_value = user
        mock_user_services_delete.side_effect = LookupError('')

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(result.status, status)
        mock_user_services_delete.assert_called_with(user)
        mock_user_services_delete.side_effect = None
