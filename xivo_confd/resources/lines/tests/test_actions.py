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
from mock import Mock, sentinel
from hamcrest import assert_that, equal_to

from xivo_dao.resources.utils.search import SearchResult

from xivo_confd.resources.lines.actions import LineServiceProxy


class TestUserResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.proxy = LineServiceProxy(self.service)
        self.items = [sentinel.item1, sentinel.item2]

    def test_when_q_param_sent_then_lines_searched_by_name(self):
        self.service.find_all_by_name.return_value = self.items
        expected_result = SearchResult(items=self.items, total=2)

        result = self.proxy.search({'q': 'myfullname'})

        self.service.find_all_by_name.assert_called_once_with('myfullname')
        assert_that(result, equal_to(expected_result))

    def test_when_no_params_sent_then_all_lines_returned(self):
        self.service.find_all.return_value = self.items
        expected_result = SearchResult(items=self.items, total=2)

        result = self.proxy.search({})

        self.service.find_all.assert_called_once_with()
        assert_that(result, equal_to(expected_result))
