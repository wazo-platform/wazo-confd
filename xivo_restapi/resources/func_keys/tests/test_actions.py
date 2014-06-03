# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_restapi.resources.func_keys import actions
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.data_handler.func_key.model import FuncKey
from mock import patch, Mock
from hamcrest import assert_that, equal_to


class TestFuncKeyActions(unittest.TestCase):

    @patch('xivo_restapi.resources.func_keys.actions.make_response')
    @patch('xivo_restapi.resources.func_keys.actions.formatter.list_to_api')
    @patch('xivo_dao.data_handler.func_key.services.search')
    @patch('xivo_restapi.resources.func_keys.actions.request')
    def test_list(self, request, func_key_search, list_to_api, make_response):
        request.args = {'limit': '1'}
        search_result = func_key_search.return_value = Mock(SearchResult)
        formatted_list = list_to_api.return_value = Mock()
        response = make_response.return_value = Mock()

        result = actions.list()

        func_key_search.assert_called_once_with(limit=1)
        list_to_api.assert_called_once_with(search_result.items, search_result.total)
        make_response.assert_called_once_with(formatted_list, 200)
        assert_that(result, equal_to(response))

    @patch('xivo_restapi.resources.func_keys.actions.make_response')
    @patch('xivo_restapi.resources.func_keys.actions.formatter.to_api')
    @patch('xivo_dao.data_handler.func_key.services.get')
    def test_get(self, func_key_get, formatter_to_api, make_response):
        func_key_id = 1

        func_key = func_key_get.return_value = Mock(FuncKey)
        formatted_func_key = formatter_to_api.return_value = Mock()
        response = make_response.return_value = Mock()

        result = actions.get(func_key_id)

        func_key_get.assert_called_once_with(func_key_id)
        formatter_to_api.assert_called_once_with(func_key)
        make_response.assert_called_once_with(formatted_func_key, 200)
        assert_that(result, equal_to(response))
