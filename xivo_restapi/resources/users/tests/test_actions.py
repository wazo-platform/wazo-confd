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

from mock import patch

from xivo_dao.data_handler.user.model import User
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/users"


class TestUserActions(TestResources):

    def build_item(self, user):
        return {
            'id': user.id,
            'firstname': user.firstname,
            'lastname': user.lastname,
            'caller_id': user.caller_id,
            'username': user.username,
            'password': user.password,
            'outgoing_caller_id': user.outgoing_caller_id,
            'description': user.description,
            'language': user.language,
            'timezone': user.timezone,
            'mobile_phone_number': user.mobile_phone_number,
            'userfield': user.userfield,
            'music_on_hold': user.music_on_hold,
            'preprocess_subroutine': user.preprocess_subroutine,
            'links': [{
                'href': 'http://localhost/1.1/users/%d' % user.id,
                'rel': 'users'
            }]
        }

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_with_no_users(self, mock_user_services_find_all):
        expected_response = {'total': 0, 'items': []}

        mock_user_services_find_all.return_value = []

        response = self.app.get(BASE_URL)

        mock_user_services_find_all.assert_any_call()
        self.assert_response_for_list(response, expected_response)

    @patch('xivo_dao.data_handler.user.services.find_all')
    def test_list_users_with_two_users(self, mock_user_services_find_all):
        user1 = User(id=1,
                     firstname=u'test1',
                     caller_id=u'"test1 "')
        user2 = User(id=2,
                     firstname=u'test2',
                     caller_id=u'"test2 "')

        expected_response = {'total': 2,
                             'items': [self.build_item(user1),
                                       self.build_item(user2)]}

        mock_user_services_find_all.return_value = [user1, user2]

        response = self.app.get(BASE_URL)

        mock_user_services_find_all.assert_any_call()
        self.assert_response_for_list(response, expected_response)

    @patch('xivo_dao.data_handler.user.services.find_all_by_fullname')
    def test_list_users_with_search(self, mock_user_services_find_all_by_fullname):
        search = 'bob'
        user = User(id=1,
                    firstname=u'Bob',
                    caller_id=u'"Bob "')

        expected_response = {'total': 1,
                             'items': [self.build_item(user)]}

        mock_user_services_find_all_by_fullname.return_value = [user]

        response = self.app.get("%s?q=%s" % (BASE_URL, search))

        mock_user_services_find_all_by_fullname.assert_called_once_with(search)
        self.assert_response_for_list(response, expected_response)

    @patch('xivo_dao.data_handler.user.services.get')
    def test_get(self, mock_user_services_get):
        user = User(id=1,
                    firstname=u'Bob',
                    caller_id=u'"Bob "')

        expected_response = self.build_item(user)

        mock_user_services_get.return_value = user

        response = self.app.get("%s/%d" % (BASE_URL, user.id))

        mock_user_services_get.assert_called_once_with(user.id)
        self.assert_response_for_get(response, expected_response)

    @patch('xivo_dao.data_handler.user.services.create')
    def test_create(self, user_create):
        user = User(firstname=u'André',
                    lastname=u'Dupond')
        user_create.return_value = created_user = User(id=1,
                                                       firstname=u'André',
                                                       lastname=u'Dupond',
                                                       caller_id=u'"André Dupond"')

        expected_response = self.build_item(created_user)

        data_serialized = self._serialize_encode({'firstname': 'André',
                                                  'lastname': 'Dupond'})
        response = self.app.post(BASE_URL, data=data_serialized)

        user_create.assert_called_once_with(user)
        self.assert_response_for_create(response, expected_response)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.edit')
    def test_edit(self, mock_user_services_edit, mock_user_services_get):
        mock_user_services_get.return_value = User(id=1,
                                                   firstname=u'Bob',
                                                   lastname=u'Simth')
        updated_user = User(id=1,
                            firstname=u'André',
                            lastname=u'Dupond',
                            description=u'éà:;')

        data = {
            'firstname': 'André',
            'lastname': 'Dupond',
            'description': 'éà:;'
        }
        data_serialized = self._serialize_encode(data)
        response = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        mock_user_services_edit.assert_called_once_with(updated_user)
        self.assert_response_for_update(response)

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user.services.delete')
    def test_delete_success(self, mock_user_services_delete, mock_user_services_get):
        mock_user_services_get.return_value = user = User(id=1, firstname=u'Bob')

        response = self.app.delete("%s/1" % BASE_URL)

        mock_user_services_delete.assert_called_with(user)
        self.assert_response_for_delete(response)
