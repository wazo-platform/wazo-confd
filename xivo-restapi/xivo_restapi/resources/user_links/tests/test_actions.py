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
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError, NonexistentParametersError
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/user_links"


class TestULEActions(TestResources):

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_with_no_ules(self, mock_ule_services_find_all):
        status_code = 200
        expected_result = '{"items": [], "total": 0}'

        mock_ule_services_find_all.return_value = []

        result = self.app.get(BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, result.data)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_with_two_ules(self, mock_ule_services_find_all):
        status_code = 200
        expected_result = '{"items": [{"line_id": 5, "user_id": 4, "extension_id": 6, "links": [{"href": "http://localhost/1.1/user_links/1", "rel": "user_links"}, {"href": "http://localhost/1.1/users/4", "rel": "users"}, {"href": "http://localhost/1.1/lines/5", "rel": "lines"}, {"href": "http://localhost/1.1/extensions/6", "rel": "extensions"}], "id": 1}, {"line_id": 8, "user_id": 7, "extension_id": 9, "links": [{"href": "http://localhost/1.1/user_links/2", "rel": "user_links"}, {"href": "http://localhost/1.1/users/7", "rel": "users"}, {"href": "http://localhost/1.1/lines/8", "rel": "lines"}, {"href": "http://localhost/1.1/extensions/9", "rel": "extensions"}], "id": 2}], "total": 2}'

        ule1 = UserLineExtension(id=1,
                                 user_id=4,
                                 line_id=5,
                                 extension_id=6)
        ule2 = UserLineExtension(id=2,
                                 user_id=7,
                                 line_id=8,
                                 extension_id=9)
        mock_ule_services_find_all.return_value = [ule1, ule2]

        result = self.app.get(BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, result.data)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_error(self, mock_ule_services_find_all):
        status_code = 500

        mock_ule_services_find_all.side_effect = Exception

        result = self.app.get(BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get(self, mock_ule_services_get):
        status_code = 200
        expected_result = '{"line_id": 5, "user_id": 5, "extension_id": 9, "links": [{"href": "http://localhost/1.1/user_links/1", "rel": "user_links"}, {"href": "http://localhost/1.1/users/5", "rel": "users"}, {"href": "http://localhost/1.1/lines/5", "rel": "lines"}, {"href": "http://localhost/1.1/extensions/9", "rel": "extensions"}], "id": 1}'

        ule = UserLineExtension(id=1,
                                user_id=5,
                                line_id=5,
                                extension_id=9)
        mock_ule_services_get.return_value = ule

        result = self.app.get("%s/1" % BASE_URL)

        mock_ule_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, result.data)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get_error(self, mock_ule_services_get):
        status_code = 500

        mock_ule_services_get.side_effect = Exception

        result = self.app.get("%s/1" % BASE_URL)

        mock_ule_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get_not_found(self, mock_ule_services_get):
        status_code = 404

        mock_ule_services_get.side_effect = ElementNotExistsError('ule')

        result = self.app.get("%s/1" % BASE_URL)

        mock_ule_services_get.assert_called_with(1)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create(self, mock_ule_services_create, formatter):
        status_code = 201
        expected_result = '{"id": 1, "links": [{"href": "http://localhost/1.1/user_links/1", "rel": "user_links"}, {"href": "http://localhost/1.1/users/2", "rel": "users"}, {"href": "http://localhost/1.1/lines/3", "rel": "lines"}, {"href": "http://localhost/1.1/extensions/4", "rel": "extensions"}]}'

        ule = UserLineExtension(id=1,
                                user_id=2,
                                line_id=3,
                                extension_id=4)
        mock_ule_services_create.return_value = ule
        formatter.to_api.return_value = expected_result

        data = '{"user_id": 2, "line_id": 3, "extension_id": 4}'

        result = self.app.post(BASE_URL, data=data)

        formatter.to_model.assert_called_with(data)
        formatter.to_api.assert_called_with(ule)
        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_result, result.data)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_error(self, mock_ule_services_create):
        status_code = 500

        data = '{"user_id": 3, "line_id": 6, "extension_id": 4}'

        mock_ule_services_create.side_effect = Exception

        result = self.app.post(BASE_URL, data=data)

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_nonexistient_paramters_error(self, mock_ule_services_create):
        status_code = 400

        data = '{"user_id": 3, "line_id": 6, "extension_id": 4}'

        mock_ule_services_create.side_effect = NonexistentParametersError()

        result = self.app.post(BASE_URL, data=data)

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_request_error(self, mock_ule_services_create):
        status_code = 400
        expected_result = '["Missing parameters: user_id"]'

        mock_ule_services_create.side_effect = MissingParametersError(['user_id'])

        data = '{"user_id": 3, "line_id": 6, "extension_id": 4}'

        result = self.app.post(BASE_URL, data=data)

        self.assertEqual(status_code, result.status_code)
        self.assertEquals(expected_result, result.data)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit(self, mock_ule_services_edit, mock_ule_services_get, formatter):
        status_code = 204
        expected_data = ''

        data = '{"lastname": "Dupond", "description": "éà":;", "firstname": "André"}'

        mock_ule_services_get.return_value = ule = Mock(UserLineExtension)

        result = self.app.put("%s/1" % BASE_URL, data=data)

        formatter.to_model_update.assert_called_with(data, ule)
        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit_error(self, mock_ule_services_edit, mock_ule_services_get, formatter):
        status_code = 500

        data = '{"lastname": "Dupond", "description": "éà":;", "firstname": "André"}'

        mock_ule_services_get.return_value = ule = Mock(UserLineExtension)
        mock_ule_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=data)

        formatter.to_model_update.assert_called_with(data, ule)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_restapi.resources.user_links.actions.formatter')
    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit_not_found(self, mock_ule_services_edit, mock_ule_services_get, formatter):
        status_code = 404

        data = '{"lastname": "Dupond", "description": "éà":;", "firstname": "André"}'

        mock_ule_services_get.return_value = Mock(UserLineExtension)
        mock_ule_services_edit.side_effect = ElementNotExistsError('ule')

        result = self.app.put("%s/1" % BASE_URL, data=data)

        self.assertEqual(status_code, result.status_code)
        self.assertEquals(formatter.call_count, 0)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.delete')
    def test_delete_success(self, mock_ule_services_delete, mock_ule_services_get):
        status_code = 204
        expected_data = ''

        ule = Mock(UserLineExtension)
        mock_ule_services_get.return_value = ule
        mock_ule_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)
        mock_ule_services_delete.assert_called_with(ule)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.delete')
    def test_delete_not_found(self, mock_ule_services_delete, mock_ule_services_get):
        status_code = 404

        ule = Mock(UserLineExtension)
        mock_ule_services_get.return_value = ule
        mock_ule_services_delete.side_effect = ElementNotExistsError('ule')

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        mock_ule_services_delete.assert_called_with(ule)
