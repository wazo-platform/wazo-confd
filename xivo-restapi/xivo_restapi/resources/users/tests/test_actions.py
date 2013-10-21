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

from mock import Mock, patch
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/users"


class TestUserActions(TestResources):

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_with_no_users(self, mock_user_services_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_user_services_find_all.return_value = []

        result = self.app.get(BASE_URL)

        mock_user_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_with_two_users(self, mock_user_services_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': 1,
                    'firstname': 'test1',
                    'lastname': '',
                    'callerid': '"test1 "',
                    'username': None,
                    'password': None,
                    'outcallerid': None,
                    'description': None,
                    'language': None,
                    'timezone': None,
                    'mobilephonenumber': None,
                    'userfield': None,
                    'musiconhold': None,
                    'links': [{
                        'href': 'http://localhost/1.1/users/1',
                        'rel': 'users'
                    }]
                },
                {
                    'id': 2,
                    'firstname': 'test2',
                    'lastname': '',
                    'callerid': '"test2 "',
                    'username': None,
                    'password': None,
                    'outcallerid': None,
                    'description': None,
                    'language': None,
                    'timezone': None,
                    'mobilephonenumber': None,
                    'userfield': None,
                    'musiconhold': None,
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

        mock_user_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.services.find_all_by_fullname')
    def test_list_users_with_search(self, mock_user_services_find_all_by_fullname):
        user_id = 1
        firstname = 'Bob'
        search = 'bob'
        expected_status_code = 200
        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': user_id,
                    'firstname': firstname,
                    'lastname': '',
                    'username': None,
                    'password': None,
                    'outcallerid': None,
                    'description': None,
                    'language': None,
                    'timezone': None,
                    'mobilephonenumber': None,
                    'userfield': None,
                    'musiconhold': None,
                    'callerid': '"%s "' % firstname,
                    'links': [{
                        'href': 'http://localhost/1.1/users/%d' % user_id,
                        'rel': 'users'
                    }]}
            ]
        }

        user = User(id=user_id,
                    firstname=firstname)
        mock_user_services_find_all_by_fullname.return_value = [user]

        result = self.app.get("%s?q=%s" % (BASE_URL, search))

        mock_user_services_find_all_by_fullname.assert_called_once_with(search)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.services.get')
    def test_get(self, mock_user_services_get):
        user_id = 1
        firstname = 'test1'
        expected_status_code = 200
        expected_result = {
            'id': user_id,
            'firstname': firstname,
            'lastname': '',
            'username': None,
            'password': None,
            'outcallerid': None,
            'description': None,
            'language': None,
            'timezone': None,
            'mobilephonenumber': None,
            'userfield': None,
            'musiconhold': None,
            'callerid': '"%s "' % firstname,
            'links': [{
                'href': 'http://localhost/1.1/users/%d' % user_id,
                'rel': 'users'
            }]
        }
        user = User(id=user_id,
                    firstname=firstname)
        mock_user_services_get.return_value = user

        result = self.app.get("%s/%d" % (BASE_URL, user_id))

        mock_user_services_get.assert_called_once_with(user_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_list_lines_associated_to_a_user_with_no_lines(self, ule_find_all_by_user_id):
        user_id = 1
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        ule_find_all_by_user_id.return_value = []

        result = self.app.get("%s/%d/user_links" % (BASE_URL, user_id))

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_list_lines_associated_to_a_user(self, ule_find_all_by_user_id):
        expected_status_code = 200
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

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_user_id')
    def test_list_lines_associated_to_a_user_with_two_line(self, ule_find_all_by_user_id):
        expected_status_code = 200
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

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.users.actions.formatter')
    @patch('xivo_dao.data_handler.user.services.create')
    def test_create(self, mock_user_services_create, formatter):
        user_id = 1
        expected_status_code = 201
        expected_result = {
            'id': user_id,
            'links': [{
                'href': 'http://localhost/1.1/users/%d' % user_id,
                'rel': 'users'
            }]
        }

        user = User(id=user_id)
        mock_user_services_create.return_value = user
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            'firstname': 'André',
            'lastname': 'Dupond'
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_with(data_serialized)
        formatter.to_api.assert_called_with(user)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.users.actions.formatter')
    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit(self, mock_user_services_edit, mock_user_services_get, formatter):
        expected_status_code = 204
        expected_result = ''

        data = {
            'firstname': 'André',
            'lastname': 'Dupond',
            'description': 'éà":;'
        }
        data_serialized = self._serialize_encode(data)

        mock_user_services_get.return_value = user = Mock(User)

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        formatter.update_model.assert_called_with(data_serialized, user)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_success(self, mock_user_services_delete, mock_user_services_get):
        expected_status_code = 204
        expected_result = ''

        user = Mock(User)
        mock_user_services_get.return_value = user
        mock_user_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        mock_user_services_delete.assert_called_with(user)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_result))
