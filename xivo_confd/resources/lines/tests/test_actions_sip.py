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
from hamcrest import assert_that, equal_to, has_property

from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.line.model import LineSIP

from xivo_confd.resources.lines.actions_sip import LineSIPServiceProxy


class TestUserResource(unittest.TestCase):

    def setUp(self):
        self.service = Mock()
        self.proxy = LineSIPServiceProxy(self.service)
        self.items = [sentinel.item1, sentinel.item2]

    def test_when_searching_then_returns_sip_lines(self):
        self.service.find_all_by_protocol.return_value = self.items
        expected = SearchResult(items=self.items, total=len(self.items))

        result = self.proxy.search({})

        assert_that(result, equal_to(expected))
        self.service.find_all_by_protocol.assert_called_once_with('sip')

    def test_when_getting_item_then_uses_service(self):
        expected = self.service.get.return_value

        result = self.proxy.get(sentinel.line_id)

        assert_that(result, equal_to(expected))
        self.service.get.assert_called_once_with(sentinel.line_id)

    def test_when_creating_then_fixes_attributes_on_model(self):
        line = LineSIP(username='myusername')
        attributes = ['id',
                      'number',
                      'context',
                      'protocol',
                      'protocolid',
                      'callerid',
                      'device_id',
                      'provisioning_extension',
                      'configregistrar',
                      'device_slot']

        self.proxy.create(line)

        created_line = self.service.create.call_args[0][0]

        assert_that(line.name, equal_to('myusername'))
        for attribute in attributes:
            assert_that(created_line, has_property(attribute, None))

    def test_when_editing_then_fixes_username_on_model(self):
        line = LineSIP(username='myusername')

        self.proxy.edit(line)

        edited_line = self.service.edit.call_args[0][0]

        assert_that(edited_line.name, equal_to('myusername'))

    def test_when_deleting_line_then_deletes_using_service(self):
        self.proxy.delete(sentinel.line)

        self.service.delete.assert_called_once_with(sentinel.line)
