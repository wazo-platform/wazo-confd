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
from xivo_restapi import flask_http_server
from xivo_restapi.helpers import serializer
from xivo_dao.data_handler.extension.model import Extension
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError

BASE_URL = "/1.1/extensions"


class TestExtensionActions(unittest.TestCase):

    def setUp(self):
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    @patch('xivo_dao.data_handler.extension.services.find_all')
    def test_list_extensions_with_no_extensions(self, mock_extension_services_find_all):
        status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_extension_services_find_all.return_value = []

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_extension_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.extension.services.find_all')
    def test_list_extensions_with_two_extensions(self, mock_extension_services_find_all):
        status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {'id': 1,
                 'exten': '1324'},
                {'id': 2,
                 'exten': '1325'}
            ]
        }

        extension1 = Extension(id=1,
                               exten='1324')
        extension2 = Extension(id=2,
                               exten='1325')
        mock_extension_services_find_all.return_value = [extension1, extension2]

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_extension_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.extension.services.find_by_exten')
    def test_list_extensions_with_search(self, mock_extension_services_find_by_exten):
        status_code = 200
        search = 'bob'

        expected_result = {
            'total': 1,
            'items': [
                {'id': 1,
                 'exten': '1324'}
            ]
        }

        extension = Extension(id=1, exten='1324')
        mock_extension_services_find_by_exten.return_value = [extension]

        result = self.app.get("%s/?q=%s" % (BASE_URL, search))
        decoded_result = serializer.decode(result.data)

        mock_extension_services_find_by_exten.assert_called_once_with(search)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.extension.services.find_all')
    def test_list_extensions_error(self, mock_extension_services_find_all):
        status_code = 500

        mock_extension_services_find_all.side_effect = Exception

        result = self.app.get("%s/" % BASE_URL)

        mock_extension_services_find_all.assert_any_call()
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.extension.services.get')
    def test_get(self, mock_extension_services_get):
        status_code = 200
        expected_result = {
            'id': 1,
            'exten': '1324'
        }

        extension = Extension(id=1, exten='1324')
        mock_extension_services_get.return_value = extension

        result = self.app.get("%s/1" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_extension_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.extension.services.get')
    def test_get_error(self, mock_extension_services_get):
        status_code = 500

        mock_extension_services_get.side_effect = Exception

        result = self.app.get("%s/1" % BASE_URL)

        mock_extension_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)

    @patch('xivo_dao.data_handler.extension.services.get')
    def test_get_not_found(self, mock_extension_services_get):
        status_code = 404

        mock_extension_services_get.side_effect = ElementNotExistsError('extension')

        result = self.app.get("%s/1" % BASE_URL)

        mock_extension_services_get.assert_called_with(1)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.extension.services.create')
    def test_create(self, mock_extension_services_create):
        status_code = 201
        expected_result = {'id': 1}

        extension = Mock(Extension)
        extension.id = 1
        mock_extension_services_create.return_value = extension

        data = {
            'exten': '1324',
            'context': 'jd'
        }

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        mock_extension_services_create.assert_called_with(Extension.from_data_source(data))
        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.extension.services.create')
    def test_create_error(self, mock_extension_services_create):
        status_code = 500

        data = {
            'exten': '1324',
            'context': 'jd'
        }

        mock_extension_services_create.side_effect = Exception

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.extension.services.create')
    def test_create_request_error(self, mock_extension_services_create):
        status_code = 400
        expected_result = ["Missing parameters: lastname"]

        mock_extension_services_create.side_effect = MissingParametersError(["lastname"])

        data = {
            'exten': '1324'
        }

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        self.assertEqual(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.edit')
    def test_edit(self, mock_extension_services_edit, mock_extension_services_get):
        status_code = 204
        expected_data = ''

        data = {
            'exten': '1324',
            'context': 'jd'
        }

        mock_extension_services_get.return_value = Mock(Extension)

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.edit')
    def test_edit_error(self, mock_extension_services_edit, mock_extension_services_get):
        status_code = 500

        data = {
            'exten': '1324',
            'context': 'jd'
        }

        mock_extension_services_get.return_value = extension = Mock(Extension)
        mock_extension_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        extension.update_from_data.assert_called_with(data)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.edit')
    def test_edit_not_found(self, mock_extension_services_edit, mock_extension_services_get):
        status_code = 404

        data = {
            'exten': '1324',
            'context': 'jd'
        }

        mock_extension_services_get.return_value = Mock(Extension)
        mock_extension_services_edit.side_effect = ElementNotExistsError('extension')

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.delete')
    def test_delete_success(self, mock_extension_services_delete, mock_extension_services_get):
        status_code = 204
        expected_data = ''

        extension = Mock(Extension)
        mock_extension_services_get.return_value = extension
        mock_extension_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)
        mock_extension_services_delete.assert_called_with(extension)

    @patch('xivo_dao.data_handler.extension.services.get')
    @patch('xivo_dao.data_handler.extension.services.delete')
    def test_delete_not_found(self, mock_extension_services_delete, mock_extension_services_get):
        status_code = 404

        extension = Mock(Extension)
        mock_extension_services_get.return_value = extension
        mock_extension_services_delete.side_effect = ElementNotExistsError('extension')

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        mock_extension_services_delete.assert_called_with(extension)
