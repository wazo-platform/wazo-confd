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
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.line.model import Line
from xivo_dao.data_handler.exception import ElementNotExistsError
from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.user_line_extension.model import UserLineExtension

BASE_URL = "/1.1/lines"


class TestLineActions(TestResources):

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_with_no_lines(self, mock_line_services_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_line_services_find_all.return_value = []

        result = self.app.get(BASE_URL)

        mock_line_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_with_two_lines(self, mock_line_services_find_all):
        expected_status_code = 200
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

        result = self.app.get(BASE_URL)

        mock_line_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line.services.find_all_by_name')
    def test_list_lines_with_search(self, mock_line_services_find_all_by_name):
        line = Line(id=1,
                    name='Bob')

        expected_status_code = 200
        search = 'bob'

        expected_result = {
            'total': line.id,
            'items': [
                {
                    'id': 1,
                    'name': 'Bob',
                    'links': [{
                        'href': 'http://localhost/1.1/lines/%d' % line.id,
                        'rel': 'lines'
                    }]
                }
            ]
        }

        mock_line_services_find_all_by_name.return_value = [line]

        result = self.app.get("%s?q=%s" % (BASE_URL, search))

        mock_line_services_find_all_by_name.assert_called_once_with(search)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_error(self, mock_line_services_find_all):
        expected_status_code = 500

        mock_line_services_find_all.side_effect = Exception

        result = self.app.get(BASE_URL)

        mock_line_services_find_all.assert_any_call()
        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_line_id')
    def test_list_user_links_not_found(self, mock_ule_services_find_all_by_line_id):
        line_id = 1370
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        mock_ule_services_find_all_by_line_id.return_value = []

        result = self.app.get("%s/%d/user_links" % (BASE_URL, line_id))

        mock_ule_services_find_all_by_line_id.assert_called_once_with(line_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_line_id')
    def test_list_user_links(self, mock_ule_services_find_all_by_line_id):
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

        mock_ule_services_find_all_by_line_id.return_value = [
            UserLineExtension(id=user_link_id,
                              user_id=user_id,
                              line_id=line_id,
                              extension_id=extension_id,
                              main_user=True,
                              main_line=True)
        ]

        result = self.app.get("%s/%d/user_links" % (BASE_URL, line_id))

        mock_ule_services_find_all_by_line_id.assert_called_once_with(line_id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.user_line_extension.services.find_all_by_line_id')
    def test_list_user_links_error(self, mock_ule_services_find_all_by_line_id):
        expected_status_code = 500

        mock_ule_services_find_all_by_line_id.side_effect = Exception

        result = self.app.get("%s/%d/user_links" % (BASE_URL, 1))

        mock_ule_services_find_all_by_line_id.assert_called_once_with(1)
        self.assertEqual(expected_status_code, result.status_code)

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get(self, mock_line_services_get):
        line = Line(id=1,
                    name='test1')

        expected_status_code = 200
        expected_result = {
            'id': line.id,
            'name': 'test1',
            'links': [{
                'href': 'http://localhost/1.1/lines/%d' % line.id,
                'rel': 'lines'
            }]
        }

        mock_line_services_get.return_value = line

        result = self.app.get("%s/%d" % (BASE_URL, line.id))

        mock_line_services_get.assert_called_with(line.id)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get_error(self, mock_line_services_get):
        line_id = 345
        expected_status_code = 500

        mock_line_services_get.side_effect = Exception

        result = self.app.get("%s/%d" % (BASE_URL, line_id))

        mock_line_services_get.assert_called_with(line_id)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get_not_found(self, mock_line_services_get):
        line_id = 3453345
        expected_status_code = 404

        mock_line_services_get.side_effect = ElementNotExistsError('line')

        result = self.app.get("%s/%d" % (BASE_URL, line_id))

        mock_line_services_get.assert_called_with(line_id)
        self.assertEqual(expected_status_code, result.status_code)
