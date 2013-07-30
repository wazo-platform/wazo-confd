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
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError

BASE_URL = "/1.1/user_links"


class TestULEActions(unittest.TestCase):

    def setUp(self):
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_with_no_ules(self, mock_ule_services_find_all):
        status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_ule_services_find_all.return_value = []

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_ule_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_with_two_ules(self, mock_ule_services_find_all):
        status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': 1,
                    'user_id': 4,
                    'links': [{
                            'href': 'http://localhost/1.1/user_links/1',
                            'rel': 'user_links'
                    }]
                 },
                 {
                    'id': 2,
                    'user_id': 5,
                    'links': [{
                            'href': 'http://localhost/1.1/user_links/2',
                            'rel': 'user_links'
                    }]
                 }
            ]
        }

        ule1 = UserLineExtension(id=1,
                                 user_id=4)
        ule2 = UserLineExtension(id=2,
                                 user_id=5)
        mock_ule_services_find_all.return_value = [ule1, ule2]

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_ule_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all')
    def test_list_ules_error(self, mock_ule_services_find_all):
        status_code = 500

        mock_ule_services_find_all.side_effect = Exception

        result = self.app.get("%s/" % BASE_URL)

        mock_ule_services_find_all.assert_any_call()
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    def test_get(self, mock_ule_services_get):
        status_code = 200
        expected_result = {
            'id': 1,
            'user_id': 5
        }

        ule = UserLineExtension(id=1,
                                user_id=5)
        mock_ule_services_get.return_value = ule

        result = self.app.get("%s/1" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_ule_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

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

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create(self, mock_ule_services_create):
        status_code = 201
        expected_result = {
            'id': 1,
            'links': [{
                'href': 'http://localhost/1.1/user_links/1',
                'rel': 'user_links'
            }]
        }

        ule = Mock(UserLineExtension)
        ule.id = 1
        mock_ule_services_create.return_value = ule

        data = {
            'user_id': 3,
            'line_id': 6,
            'extension_id': 4
        }

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        mock_ule_services_create.assert_called_with(UserLineExtension.from_user_data(data))
        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_error(self, mock_ule_services_create):
        status_code = 500

        data = {'user_id': 3}

        mock_ule_services_create.side_effect = Exception

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.create')
    def test_create_request_error(self, mock_ule_services_create):
        status_code = 400
        expected_result = ["Missing parameters: user_id"]

        mock_ule_services_create.side_effect = MissingParametersError(["user_id"])

        data = {'user_id': 4}

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        self.assertEqual(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit(self, mock_ule_services_edit, mock_ule_services_get):
        status_code = 204
        expected_data = ''

        data = {u'id': 1,
                u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}

        mock_ule_services_get.return_value = Mock(UserLineExtension)

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit_error(self, mock_ule_services_edit, mock_ule_services_get):
        status_code = 500

        data = {u'firstname': u'André',
                u'lastname': u'Dupond',
                u'description': u'éà":;'}

        mock_ule_services_get.return_value = ule = Mock(UserLineExtension)
        mock_ule_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        ule.update_from_data.assert_called_with(data)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.get')
    @patch('xivo_dao.data_handler.user_line_extension.services.edit')
    def test_edit_not_found(self, mock_ule_services_edit, mock_ule_services_get):
        status_code = 404

        data = {'firstname': 'André',
                'lastname': 'Dupond',
                'description': 'éà":;'}

        mock_ule_services_get.return_value = Mock(UserLineExtension)
        mock_ule_services_edit.side_effect = ElementNotExistsError('ule')

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

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
