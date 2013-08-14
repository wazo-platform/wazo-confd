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
from hamcrest import assert_that, equal_to, has_entries

from xivo_restapi import flask_http_server
from xivo_restapi.helpers import serializer
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension

BASE_URL = "/1.1/users"


class TestUserActions(unittest.TestCase):

    def setUp(self):
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_with_no_users(self, mock_user_services_find_all):
        status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_user_services_find_all.return_value = []

        result = self.app.get(BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_user_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_with_two_users(self, mock_user_services_find_all):
        status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': 1,
                    'firstname': 'test1',
                    'links': [{
                        'href': 'http://localhost/1.1/users/1',
                        'rel': 'users'
                    }]
                },
                {
                    'id': 2,
                    'firstname': 'test2',
                    'links': [{
                        'href': 'http://localhost/1.1/users/2',
                        'rel': 'users'
                    }]
                }
            ]
        }

        user1 = User(id=1,
                     firstname='test1')
        user2 = User(id=2,
                     firstname='test2')
        mock_user_services_find_all.return_value = [user1, user2]

        result = self.app.get(BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_user_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user.services.find_all_by_fullname')
    def test_list_users_with_search(self, mock_user_services_find_all_by_fullname):
        status_code = 200
        search = 'bob'

        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': 1,
                    'firstname': 'Bob',
                    'links': [{
                        'href': 'http://localhost/1.1/users/1',
                        'rel': 'users'
                    }]}
            ]
        }

        user = User(id=1, firstname='Bob')
        mock_user_services_find_all_by_fullname.return_value = [user]

        result = self.app.get("%s?q=%s" % (BASE_URL, search))
        decoded_result = serializer.decode(result.data)

        mock_user_services_find_all_by_fullname.assert_called_once_with(search)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_error(self, mock_user_services_find_all):
        status_code = 500

        mock_user_services_find_all.side_effect = Exception

        result = self.app.get(BASE_URL)

        mock_user_services_find_all.assert_any_call()
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user.services.get')
    def test_get(self, mock_user_services_get):
        status_code = 200
        expected_result = {
            'id': 1,
            'firstname': 'test1'
        }

        user = User(id=1, firstname='test1')
        mock_user_services_get.return_value = user

        result = self.app.get("%s/1" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_user_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user.services.get')
    def test_get_error(self, mock_user_services_get):
        status_code = 500

        mock_user_services_get.side_effect = Exception

        result = self.app.get("%s/1" % BASE_URL)

        mock_user_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user.services.get')
    def test_get_not_found(self, mock_user_services_get):
        status_code = 404

        mock_user_services_get.side_effect = ElementNotExistsError('user')

        result = self.app.get("%s/1" % BASE_URL)

        mock_user_services_get.assert_called_with(1)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_list_lines_associated_to_a_user_with_no_lines(self, ule_find_all_by_user_id):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        user_id = 1

        ule_find_all_by_user_id.return_value = []

        result = self.app.get("%s/%d/user_links" % (BASE_URL, user_id))
        decoded_result = serializer.decode(result.data)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(decoded_result, equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_list_lines_associated_to_a_user(self, ule_find_all_by_user_id):
        status_code = 200
        user_link_id = 83
        user_id = 14
        line_id = 42324
        extension_id = 2132

        expected_result = {
            "total": 1,
            "items": [
                {
                    "id": user_link_id,
                    "user_id": user_id,
                    "line_id": line_id,
                    "extension_id": extension_id,
                    "main_user": True,
                    "main_line": True,
                    "links": [
                        {
                            "rel": "user_links",
                            "href": "http://localhost/1.1/user_links/%d" % user_link_id
                        },
                        {
                            "rel": "users",
                            "href": "http://localhost/1.1/users/%d" % user_id
                        },
                        {
                            "rel": "lines",
                            "href": "http://localhost/1.1/lines/%d" % line_id
                        },
                        {
                            "rel": "extensions",
                            "href": "http://localhost/1.1/extensions/%d" % extension_id
                        }
                    ]
                }
            ]
        }

        ule_find_all_by_user_id.return_value = [
            UserLineExtension(id=user_link_id,
                              user_id=user_id,
                              line_id=line_id,
                              extension_id=extension_id,
                              main_user=True,
                              main_line=True)
        ]

        result = self.app.get("%s/%d/user_links" % (BASE_URL, user_id))

        decoded_result = serializer.decode(result.data)

        assert_that(result.status_code, equal_to(status_code))
        assert_that(decoded_result, has_entries(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_list_lines_associated_to_a_user_with_two_line(self, ule_find_all_by_user_id):
        status_code = 200
        user_link_id = 83
        user_id = 14
        line_id_1 = 42324
        line_id_2 = 25698
        extension_id = 2132

        expected_result = {
            "total": 2,
            "items": [
                {
                    "id": user_link_id,
                    "user_id": user_id,
                    "line_id": line_id_1,
                    "extension_id": extension_id,
                    "main_user": True,
                    "main_line": True,
                    "links": [
                        {
                            "rel": "user_links",
                            "href": "http://localhost/1.1/user_links/%d" % user_link_id
                        },
                        {
                            "rel": "users",
                            "href": "http://localhost/1.1/users/%d" % user_id
                        },
                        {
                            "rel": "lines",
                            "href": "http://localhost/1.1/lines/%d" % line_id_1
                        },
                        {
                            "rel": "extensions",
                            "href": "http://localhost/1.1/extensions/%d" % extension_id
                        }
                    ]
                },
                {
                    "id": user_link_id,
                    "user_id": user_id,
                    "line_id": line_id_2,
                    "extension_id": extension_id,
                    "main_user": True,
                    "main_line": True,
                    "links": [
                        {
                            "rel": "user_links",
                            "href": "http://localhost/1.1/user_links/%d" % user_link_id
                        },
                        {
                            "rel": "users",
                            "href": "http://localhost/1.1/users/%d" % user_id
                        },
                        {
                            "rel": "lines",
                            "href": "http://localhost/1.1/lines/%d" % line_id_2
                        },
                        {
                            "rel": "extensions",
                            "href": "http://localhost/1.1/extensions/%d" % extension_id
                        }
                    ]
                }
            ]
        }

        ule_find_all_by_user_id.return_value = [
            UserLineExtension(id=user_link_id,
                              user_id=user_id,
                              line_id=line_id_1,
                              extension_id=extension_id,
                              main_user=True,
                              main_line=True),
            UserLineExtension(id=user_link_id,
                              user_id=user_id,
                              line_id=line_id_2,
                              extension_id=extension_id,
                              main_user=True,
                              main_line=True)
        ]

        result = self.app.get("%s/%d/user_links" % (BASE_URL, user_id))

        decoded_result = serializer.decode(result.data)

        assert_that(result.status_code, equal_to(status_code))
        assert_that(decoded_result, has_entries(expected_result))

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create(self, mock_user_services_create):
        status_code = 201
        expected_result = {
            'id': 1,
            'links': [{
                'href': 'http://localhost/1.1/users/1',
                'rel': 'users'
            }]
        }

        user = Mock(User)
        user.id = 1
        mock_user_services_create.return_value = user

        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}

        result = self.app.post(BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        mock_user_services_create.assert_called_with(User.from_user_data(data))
        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create_error(self, mock_user_services_create):
        status_code = 500

        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        mock_user_services_create.side_effect = Exception

        result = self.app.post(BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create_request_error(self, mock_user_services_create):
        status_code = 400
        expected_result = ["Missing parameters: lastname"]

        mock_user_services_create.side_effect = MissingParametersError(["lastname"])

        data = {'firstname': 'André'}

        result = self.app.post(BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        self.assertEqual(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit(self, mock_user_services_edit, mock_user_services_get):
        status_code = 204
        expected_data = ''

        data = {u'id': 1,
                u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}

        mock_user_services_get.return_value = Mock(User)

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit_error(self, mock_user_services_edit, mock_user_services_get):
        status_code = 500

        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}

        mock_user_services_get.return_value = user = Mock(User)
        mock_user_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        user.update_from_data.assert_called_with(data)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit_not_found(self, mock_user_services_edit, mock_user_services_get):
        status_code = 404

        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        mock_user_services_get.return_value = Mock(User)
        mock_user_services_edit.side_effect = ElementNotExistsError('user')

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_success(self, mock_user_services_delete, mock_user_services_get):
        status_code = 204
        expected_data = ''

        user = Mock(User)
        mock_user_services_get.return_value = user
        mock_user_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)
        mock_user_services_delete.assert_called_with(user)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_not_found(self, mock_user_services_delete, mock_user_services_get):
        status_code = 404

        user = Mock(User)
        mock_user_services_get.return_value = user
        mock_user_services_delete.side_effect = ElementNotExistsError('user')

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        mock_user_services_delete.assert_called_with(user)
