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
from xivo_dao.data_handler.line.model import LineSIP
from xivo_dao.data_handler.exception import MissingParametersError, \
    ElementNotExistsError

BASE_URL = "/1.1/lines_sip"


class TestLineActions(unittest.TestCase):

    def setUp(self):
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    @patch('xivo_dao.data_handler.line.services.find_by_protocol')
    def test_list_lines_with_no_lines(self, mock_line_services_find_by_protocol):
        status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_line_services_find_by_protocol.return_value = []

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_line_services_find_by_protocol.assert_called_once_with('sip')
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.find_by_protocol')
    def test_list_lines_with_two_lines(self, mock_line_services_find_by_protocol):
        status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': 1,
                    'username': 'test1',
                    'links': [{
                        'href': 'http://localhost/1.1/lines_sip/1',
                        'rel': 'lines_sip'
                    }]
                },
                {
                    'id': 2,
                    'username': 'test2',
                    'links': [{
                        'href': 'http://localhost/1.1/lines_sip/2',
                        'rel': 'lines_sip'
                    }]
                }
            ]
        }

        line1 = LineSIP(id=1,
                        username='test1')
        line2 = LineSIP(id=2,
                        username='test2')
        mock_line_services_find_by_protocol.return_value = [line1, line2]

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_line_services_find_by_protocol.assert_called_once_with('sip')
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.find_by_protocol')
    def test_list_lines_error(self, mock_line_services_find_by_protocol):
        status_code = 500

        mock_line_services_find_by_protocol.side_effect = Exception

        result = self.app.get("%s/" % BASE_URL)

        mock_line_services_find_by_protocol.assert_called_once_with('sip')
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get(self, mock_line_services_get):
        status_code = 200
        expected_result = {
            'id': 1,
            'username': 'test1'
        }

        line = LineSIP(id=1, username='test1')
        mock_line_services_get.return_value = line

        result = self.app.get("%s/1" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_line_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get_error(self, mock_line_services_get):
        status_code = 500

        mock_line_services_get.side_effect = Exception

        result = self.app.get("%s/1" % BASE_URL)

        mock_line_services_get.assert_called_with(1)
        self.assertEquals(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get_not_found(self, mock_line_services_get):
        status_code = 404

        mock_line_services_get.side_effect = ElementNotExistsError('line')

        result = self.app.get("%s/1" % BASE_URL)

        mock_line_services_get.assert_called_with(1)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.create')
    def test_create(self, mock_line_services_create):
        status_code = 201
        expected_result = {
            'id': 1,
            'links': [{
                    'href': 'http://localhost/1.1/lines_sip/1',
                    'rel': 'lines_sip'
            }]
        }

        line = Mock(LineSIP)
        line.id = 1
        mock_line_services_create.return_value = line

        data = {
            'protocol': 'sip',
            'username': 'toto',
            'context': 'default'
        }

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        mock_line_services_create.assert_called_with(LineSIP.from_user_data(data))
        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.create')
    def test_create_error(self, mock_line_services_create):
        status_code = 500

        data = {
            'protocol': 'sip',
            'username': 'toto',
            'context': 'default'
        }

        mock_line_services_create.side_effect = Exception

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.create')
    def test_create_request_error(self, mock_line_services_create):
        status_code = 400
        expected_result = ["Missing parameters: context"]

        mock_line_services_create.side_effect = MissingParametersError(["context"])

        data = {
            'protocol': 'sip'
        }

        result = self.app.post("%s/" % BASE_URL, data=serializer.encode(data))
        decoded_result = serializer.decode(result.data)

        self.assertEqual(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit(self, mock_line_services_edit, mock_line_services_get):
        status_code = 204
        expected_data = ''

        data = {
            'id': 1,
            'protocol': 'sip',
            'username': 'toto',
            'context': 'default'
        }

        mock_line_services_get.return_value = Mock(LineSIP)

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit_error(self, mock_line_services_edit, mock_line_services_get):
        status_code = 500

        data = {
            'protocol': 'sip',
            'username': 'toto',
            'context': 'default'
        }

        mock_line_services_get.return_value = line = Mock(LineSIP)
        mock_line_services_edit.side_effect = Exception

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        line.update_from_data.assert_called_with(data)
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit_not_found(self, mock_line_services_edit, mock_line_services_get):
        status_code = 404

        data = {
            'protocol': 'sip',
            'username': 'toto',
            'context': 'default'
        }

        mock_line_services_get.return_value = Mock(LineSIP)
        mock_line_services_edit.side_effect = ElementNotExistsError('line')

        result = self.app.put("%s/1" % BASE_URL, data=serializer.encode(data))

        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.delete')
    def test_delete_success(self, mock_line_services_delete, mock_line_services_get):
        status_code = 204
        expected_data = ''

        line = Mock(LineSIP)
        mock_line_services_get.return_value = line
        mock_line_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        self.assertEqual(expected_data, result.data)
        mock_line_services_delete.assert_called_with(line)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.delete')
    def test_delete_not_found(self, mock_line_services_delete, mock_line_services_get):
        status_code = 404

        line = Mock(LineSIP)
        mock_line_services_get.return_value = line
        mock_line_services_delete.side_effect = ElementNotExistsError('line')

        result = self.app.delete("%s/1" % BASE_URL)

        self.assertEqual(status_code, result.status_code)
        mock_line_services_delete.assert_called_with(line)
