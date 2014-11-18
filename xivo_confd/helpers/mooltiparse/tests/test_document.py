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
from mock import Mock
from hamcrest import assert_that, equal_to, contains

from xivo_confd.helpers.mooltiparse.field import Field
from xivo_confd.helpers.mooltiparse.document import Document, DocumentProxy
from xivo_dao.data_handler.exception import InputError


class TestDocument(unittest.TestCase):

    def test_given_a_list_of_fields_when_document_validated_then_each_field_validated(self):
        field1 = Mock(Field)
        field1.name = 'field1'
        field2 = Mock(Field)
        field2.name = 'field2'

        content = {'field1': 'value1',
                   'field2': 'value2'}

        document = Document([field1, field2])
        document.validate(content)

        field1.validate.assert_called_with('value1', None)
        field2.validate.assert_called_with('value2', None)

    def test_given_a_document_when_validated_with_an_action_then_field_validated_with_action(self):
        field1 = Mock(Field)
        field1.name = 'field1'

        content = {'field1': 'value1'}

        document = Document([field1])
        document.validate(content, 'action')

        field1.validate.assert_called_with('value1', 'action')

    def test_given_a_document_then_returns_a_list_of_field_names(self):
        field1 = Mock(Field)
        field1.name = 'field1'

        field2 = Mock(Field)
        field2.name = 'field2'

        document = Document([field1, field2])

        assert_that(document.field_names(), contains('field1', 'field2'))

    def test_given_a_document_when_content_contains_unknown_field_then_raises_error(self):
        field1 = Mock(Field)
        field1.name = 'field1'

        content = {'invalidfield': 'invalidvalue'}

        document = Document([field1])

        self.assertRaises(InputError, document.validate, content)


class TestDocumentProxy(unittest.TestCase):

    def test_given_a_parser_and_document_when_request_parsed_then_parser_called(self):
        parser = Mock()
        document = Mock()
        request = Mock()

        content = parser.parse.return_value

        proxy = DocumentProxy(parser, document)
        result = proxy.parse(request, 'action')

        assert_that(result, equal_to(content))
        parser.parse.assert_called_once_with(request, document, 'action')

    def test_document_proxy_proxies_call_to_field_names(self):
        document = Mock()

        proxy = DocumentProxy(Mock(), document)

        result = proxy.field_names()

        assert_that(result, equal_to(document.field_names.return_value))
        document.field_names.assert_called_once_with()

    def test_document_proxy_proxies_call_to_validate(self):
        document = Mock()
        content = Mock()
        action = Mock()

        proxy = DocumentProxy(Mock(), document)

        proxy.validate(content, action)

        document.validate.assert_called_once_with(content, action)
