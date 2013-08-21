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

from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError, NonexistentParametersError
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/user_links"


class TestULEActions(TestResources):

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_with_no_ules(self, mock_ule_services_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_ule_services_find_all.return_value = []

        result = self.app.get(BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_with_two_ules(self, mock_ule_services_find_all):
        ule1 = UserLineExtension(id=1,
                                 user_id=4,
                                 line_id=5,
                                 extension_id=6)
        ule2 = UserLineExtension(id=2,
                                 user_id=7,
                                 line_id=8,
                                 extension_id=9)

        expected_status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': ule1.id,
                    'line_id': ule1.line_id,
                    'user_id': ule1.user_id,
                    'extension_id': ule1.extension_id,
                    'links': [
                        {'href': 'http://localhost/1.1/user_links/%d' % ule1.id, 'rel': 'user_links'},
                        {"href": 'http://localhost/1.1/users/%d' % ule1.user_id, "rel": "users"},
                        {"href": 'http://localhost/1.1/lines/%d' % ule1.line_id, 'rel': 'lines'},
                        {"href": 'http://localhost/1.1/extensions/%d' % ule1.extension_id, 'rel': 'extensions'}
                    ]
                },
                {
                    'id': ule2.id,
                    'line_id': ule2.line_id,
                    'user_id': ule2.user_id,
                    'extension_id': ule2.extension_id,
                    'links': [
                        {'href': 'http://localhost/1.1/user_links/%d' % ule2.id, 'rel': 'user_links'},
                        {"href": 'http://localhost/1.1/users/%d' % ule2.user_id, "rel": "users"},
                        {"href": 'http://localhost/1.1/lines/%d' % ule2.line_id, 'rel': 'lines'},
                        {"href": 'http://localhost/1.1/extensions/%d' % ule2.extension_id, 'rel': 'extensions'}
                    ]
                }
            ]
        }
        mock_ule_services_find_all.return_value = [ule1, ule2]

        result = self.app.get(BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_error(self, mock_ule_services_find_all):
        expected_status_code = 500

        mock_ule_services_find_all.side_effect = Exception

        result = self.app.get(BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get(self, mock_ule_services_get):
        ule = UserLineExtension(id=1,
                                user_id=5,
                                line_id=5,
                                extension_id=9)

        expected_status_code = 200
        expected_result = {
            'id': ule.id,
            'line_id': ule.line_id,
            'user_id': ule.user_id,
            'extension_id': ule.extension_id,
            'links': [
                {'href': 'http://localhost/1.1/user_links/%d' % ule.id, 'rel': 'user_links'},
                {"href": 'http://localhost/1.1/users/%d' % ule.user_id, "rel": "users"},
                {"href": 'http://localhost/1.1/lines/%d' % ule.line_id, 'rel': 'lines'},
                {"href": 'http://localhost/1.1/extensions/%d' % ule.extension_id, 'rel': 'extensions'}
            ]
        }
        mock_ule_services_get.return_value = ule

        result = self.app.get("%s/%d" % (BASE_URL, ule.id))

        mock_ule_services_get.assert_called_with(ule.id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get_error(self, mock_ule_services_get):
        ule_id = 1
        expected_status_code = 500

        mock_ule_services_get.side_effect = Exception

        result = self.app.get("%s/%d" % (BASE_URL, ule_id))

        mock_ule_services_get.assert_called_with(ule_id)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get_not_found(self, mock_ule_services_get):
        ule_id = 1
        expected_status_code = 404

        mock_ule_services_get.side_effect = ElementNotExistsError('ule')

        result = self.app.get("%s/%d" % (BASE_URL, ule_id))

        mock_ule_services_get.assert_called_with(ule_id)
        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create(self, mock_ule_services_create, formatter):
        ule = UserLineExtension(id=1,
                                user_id=2,
                                line_id=3,
                                extension_id=4)

        expected_status_code = 201
        expected_result = {
            'id': ule.id,
            'line_id': ule.line_id,
            'user_id': ule.user_id,
            'extension_id': ule.extension_id,
            'links': [
                {'href': 'http://localhost/1.1/user_links/%d' % ule.id, 'rel': 'user_links'},
                {"href": 'http://localhost/1.1/users/%d' % ule.user_id, "rel": "users"},
                {"href": 'http://localhost/1.1/lines/%d' % ule.line_id, 'rel': 'lines'},
                {"href": 'http://localhost/1.1/extensions/%d' % ule.extension_id, 'rel': 'extensions'}
            ]
        }
        mock_ule_services_create.return_value = ule
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_with(data_serialized)
        formatter.to_api.assert_called_with(ule)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.users.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_error(self, mock_ule_services_create, formatter):
        expected_status_code = 500

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        mock_ule_services_create.side_effect = Exception

        result = self.app.post(BASE_URL, data=data_serialized)

        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_nonexistient_paramters_error(self, mock_ule_services_create):
        expected_status_code = 400

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        mock_ule_services_create.side_effect = NonexistentParametersError()

        result = self.app.post(BASE_URL, data=data_serialized)

        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_request_error(self, mock_ule_services_create):
        expected_status_code = 400
        expected_result = ['Missing parameters: user_id']

        mock_ule_services_create.side_effect = MissingParametersError(['user_id'])

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        self.assertEqual(expected_status_code, result.status_code)
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit(self, mock_ule_services_edit, mock_ule_services_get, formatter):
        expected_status_code = 204
        expected_data = ''

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        mock_ule_services_get.return_value = ule = Mock(UserLineExtension)

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        formatter.update_model.assert_called_with(data_serialized, ule)
        self.assertEqual(expected_status_code, result.status_code)
        self.assertEqual(expected_data, result.data)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit_error(self, mock_ule_services_edit, mock_ule_services_get, formatter):
        expected_status_code = 500

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        mock_ule_services_get.return_value = ule = Mock(UserLineExtension)
        mock_ule_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        formatter.update_model.assert_called_with(data_serialized, ule)
        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit_not_found(self, mock_ule_services_edit, mock_ule_services_get, formatter):
        expected_status_code = 404

        data = {
            'user_id': 2,
            'line_id': 3,
            'extension_id': 4
        }
        data_serialized = self._serialize_encode(data)

        mock_ule_services_get.return_value = Mock(UserLineExtension)
        mock_ule_services_edit.side_effect = ElementNotExistsError('ule')

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        self.assertEqual(expected_status_code, result.status_code)
        self.assertEquals(formatter.call_count, 0)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.delete')
    def test_delete_success(self, mock_ule_services_delete, mock_ule_services_get):
        expected_status_code = 204
        expected_data = ''

        ule = Mock(UserLineExtension)
        mock_ule_services_get.return_value = ule
        mock_ule_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(expected_status_code, result.status_code)
        self.assertEqual(expected_data, result.data)
        mock_ule_services_delete.assert_called_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.delete')
    def test_delete_not_found(self, mock_ule_services_delete, mock_ule_services_get):
        expected_status_code = 404

        ule = Mock(UserLineExtension)
        mock_ule_services_get.return_value = ule
        mock_ule_services_delete.side_effect = ElementNotExistsError('ule')

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(expected_status_code, result.status_code)
        mock_ule_services_delete.assert_called_with(ule)
