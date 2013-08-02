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

from mock import patch
from xivo_restapi import flask_http_server
from xivo_restapi.helpers import serializer
from xivo_dao.data_handler.line.model import Line
from xivo_dao.data_handler.exception import ElementNotExistsError

BASE_URL = "/1.1/lines"


class TestLineActions(unittest.TestCase):

    def setUp(self):
        flask_http_server.register_blueprints()
        flask_http_server.app.testing = True
        self.app = flask_http_server.app.test_client()

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_with_no_lines(self, mock_line_services_find_all):
        status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_line_services_find_all.return_value = []

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_line_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_with_two_lines(self, mock_line_services_find_all):
        status_code = 200
        expected_result = {
            'total': 2,
            'items': [
                {
                    'id': 1,
                    'name': 'test1',
                    'links': [{
                            'href': 'http://localhost/1.1/lines/1',
                            'rel': 'lines'
                    }]},
                {
                    'id': 2,
                    'name': 'test2',
                    'links': [{
                            'href': 'http://localhost/1.1/lines/2',
                            'rel': 'lines'
                    }]}
            ]
        }

        line1 = Line(id=1,
                     name='test1')
        line2 = Line(id=2,
                     name='test2')
        mock_line_services_find_all.return_value = [line1, line2]

        result = self.app.get("%s/" % BASE_URL)
        decoded_result = serializer.decode(result.data)

        mock_line_services_find_all.assert_any_call()
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.find_all_by_name')
    def test_list_lines_with_search(self, mock_line_services_find_all_by_name):
        status_code = 200
        search = 'bob'

        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': 1,
                    'name': 'Bob',
                    'links': [{
                            'href': 'http://localhost/1.1/lines/1',
                            'rel': 'lines'
                    }]
                 }
            ]
        }

        line = Line(id=1, name='Bob')
        mock_line_services_find_all_by_name.return_value = [line]

        result = self.app.get("%s/?q=%s" % (BASE_URL, search))
        decoded_result = serializer.decode(result.data)

        mock_line_services_find_all_by_name.assert_called_once_with(search)
        self.assertEquals(status_code, result.status_code)
        self.assertEquals(expected_result, decoded_result)

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_error(self, mock_line_services_find_all):
        status_code = 500

        mock_line_services_find_all.side_effect = Exception

        result = self.app.get("%s/" % BASE_URL)

        mock_line_services_find_all.assert_any_call()
        self.assertEqual(status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get(self, mock_line_services_get):
        status_code = 200
        expected_result = {
            'id': 1,
            'name': 'test1'
        }

        line = Line(id=1, name='test1')
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
