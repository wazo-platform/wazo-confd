# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import Mock, patch
from hamcrest import assert_that, equal_to

from xivo_confd.resources.users.actions import UserResource


@patch('xivo_confd.resources.users.actions.request')
class TestUserResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.converter = Mock()
        self.directory_converter = Mock()
        self.resource = UserResource(self.service, self.converter, self.directory_converter)

    def test_when_request_contains_param_q_then_searches_using_fullname(self, request):
        request.args = {'q': 'myfullname'}
        expected_items = self.service.find_all_by_fullname.return_value
        expected_response = self.converter.encode_list.return_value

        response = self.resource.search()

        self.service.find_all_by_fullname.assert_called_once_with('myfullname')
        self.converter.encode_list.assert_called_once_with(expected_items)
        assert_that(response, equal_to((expected_response,
                                       200,
                                       {'Content-Type': 'application/json'})))

    def test_when_no_view_param_then_default_converter_is_used(self, request):
        request.args = {}
        expected_search = self.service.search.return_value
        expected_response = self.converter.encode_list.return_value

        response = self.resource.search()
        self.converter.encode_list.assert_called_once_with(expected_search.items,
                                                           expected_search.total)
        assert_that(response[0], equal_to(expected_response))

    def test_when_view_param_contains_directory_then_directory_converter_is_used(self, request):
        request.args = {'view': 'directory'}
        expected_search = self.service.search.return_value
        expected_response = self.directory_converter.encode_list.return_value

        response = self.resource.search()
        self.directory_converter.encode_list.assert_called_once_with(expected_search.items,
                                                                     expected_search.total)
        assert_that(response[0], equal_to(expected_response))
