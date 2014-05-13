# -*- coding: utf-8 -*-
#
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from hamcrest import assert_that, equal_to

from mock import patch, Mock
from xivo_dao.data_handler.user_line.model import UserLine
from xivo_dao.data_handler.user_line.exception import UserLineNotExistsError
from xivo_dao.data_handler.user.model import User
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_restapi.helpers.tests.test_resources import TestResources


BASE_URL = '/1.1/users/%s/lines'
DISSOCIATE_URL = BASE_URL + '/%s'


class TestUserLineActions(TestResources):

    @patch('xivo_restapi.resources.user_line.actions.formatter')
    @patch('xivo_dao.data_handler.user_line.services.associate')
    def test_associate_line(self, user_line_associate, formatter):
        user_id = 1
        line_id = 2

        expected_status_code = 201
        expected_result = {
            u'user_id': user_id,
            u'line_id': line_id,
            u'main_user': True,
            u'main_line': True,
            'links': [
                {
                    'rel': 'lines',
                    'href': 'http://localhost/1.1/lines/%s' % line_id
                },
                {
                    u'href': u'http://localhost/1.1/users/%d' % user_id,
                    u'rel': u'users'
                }
            ]
        }

        user_line = UserLine(line_id=line_id)
        user_line_associate.return_value = user_line

        formatter.to_model.return_value = user_line
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            'line_id': line_id
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL % user_id, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized, user_id)
        user_line_associate.assert_called_once_with(user_line)
        formatter.to_api.assert_called_once_with(user_line)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line.services.get_by_user_id_and_line_id')
    @patch('xivo_dao.data_handler.user_line.services.dissociate')
    def test_dissociate_line(self, user_line_dissociate, get_by_user_id_and_line_id):
        expected_status_code = 204

        user_id = 1
        line_id = 2
        get_by_user_id_and_line_id.return_value = user_line = UserLine(user_id=user_id, line_id=line_id)

        result = self.app.delete(DISSOCIATE_URL % (user_id, line_id))

        user_line_dissociate.assert_called_once_with(user_line)
        get_by_user_id_and_line_id.assert_called_once_with(user_id, line_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(""))

    @patch('xivo_dao.data_handler.user_line.services.get_by_user_id_and_line_id')
    def test_dissociate_line_when_user_line_does_not_exist(self, get_by_user_id_and_line_id):
        user_id = 1
        line_id = 2

        expected_status_code = 404
        expected_response = ['User with id=%s is not associated with line id=%s' % (user_id, line_id)]

        get_by_user_id_and_line_id.side_effect = UserLineNotExistsError.from_user_id(user_id)

        result = self.app.delete(DISSOCIATE_URL % (user_id, line_id))

        get_by_user_id_and_line_id.assert_called_once_with(user_id, line_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_response))

    @patch('xivo_dao.data_handler.user.services.get')
    def test_get_line_associated_to_a_user_when_user_does_not_exist(self, user_services_get):
        user_id = 1
        expected_status_code = 404
        expected_result = ["User with id=1 does not exist"]

        user_services_get.side_effect = ElementNotExistsError('User', id=user_id)

        result = self.app.get(BASE_URL % user_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user_line.services.find_all_by_user_id')
    def test_get_lines_associated_to_a_user_with_no_line(self, user_line_find_all_by_user_id, user_services_get):
        user_id = 1
        expected_status_code = 200
        expected_result = {u'items': [], u'total': 0}

        user_services_get.return_value = Mock(User, id=user_id)
        user_line_find_all_by_user_id.return_value = []

        result = self.app.get(BASE_URL % user_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user.services.get')
    @patch('xivo_dao.data_handler.user_line.services.find_all_by_user_id')
    def test_get_lines_associated_to_a_user(self, user_line_find_all_by_user_id, user_services_get):
        user_id = 1
        line_id = 13
        expected_status_code = 200
        expected_result = {
            u'total': 1,
            u'items': [
                {
                    u'user_id': user_id,
                    u'line_id': line_id,
                    u'main_user': True,
                    u'main_line': True,
                    u'links': [
                        {u'href': u'http://localhost/1.1/lines/%d' % line_id,
                         u'rel': u'lines'},
                        {u'href': u'http://localhost/1.1/users/%d' % user_id,
                         u'rel': u'users'}
                    ]
                }
            ]
        }

        user_line = UserLine(user_id=user_id,
                             line_id=line_id)

        user_services_get.return_value = Mock(User, id=user_id)
        user_line_find_all_by_user_id.return_value = [user_line]

        result = self.app.get(BASE_URL % user_id)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))
