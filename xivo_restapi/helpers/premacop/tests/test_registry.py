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
from hamcrest import assert_that, equal_to
from mock import Mock

from xivo_restapi.helpers.premacop.registry import ParserRegistry
from xivo_restapi.helpers.premacop.document import Document
from xivo_restapi.helpers.premacop.errors import ContentTypeError


class TestParserRegistry(unittest.TestCase):

    def setUp(self):
        self.registry = ParserRegistry()

    def test_given_no_parsers_registered_then_raises_error(self):
        self.assertRaises(ContentTypeError, self.registry.parser_for_content_type, 'content/type')

    def test_given_wrong_content_type_then_raises_error(self):
        registry = ParserRegistry()
        registry.register('application/json', Mock())

        self.assertRaises(ContentTypeError, self.registry.parser_for_content_type, 'content/type')

    def test_given_one_parser_registered_then_return_parser(self):
        content_type = 'application/json'
        parser = Mock()

        self.registry.register('application/json', parser)

        result = self.registry.parser_for_content_type(content_type)

        assert_that(result, equal_to(parser))
