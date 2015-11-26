# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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
# along with this program.  If not, see <http://www.gnu.org/licenses/>S

import unittest
import json

from mock import Mock, patch
from hamcrest import assert_that, equal_to, has_entries, has_item, contains

from xivo_confd.helpers.converter import Converter, Mapper, Serializer, Parser, Builder, LinkGenerator
from xivo_confd.helpers.converter import DocumentMapper, DocumentParser, ResourceSerializer, RequestParser, ModelBuilder
from xivo_confd.helpers.mooltiparse.document import Document, DocumentProxy


class TestConverter(unittest.TestCase):

    def setUp(self):
        self.mapper = Mock(Mapper)
        self.mapper.for_decoding.return_value = {'foo': 'bar'}

        self.serializer = Mock(Serializer)
        self.parser = Mock(Parser)
        self.builder = Mock(Builder)

        self.converter = Converter(mapper=self.mapper,
                                   serializer=self.serializer,
                                   parser=self.parser,
                                   builder=self.builder)

    def test_when_encoding_then_maps_model_using_mapper(self):
        model = Mock()

        self.converter.encode(model)

        self.mapper.for_encoding.assert_called_once_with(model)

    def test_when_encoding_then_serializes_mapping(self):
        model = Mock()
        mapped_model = self.mapper.for_encoding.return_value
        serialized_model = self.serializer.serialize.return_value

        result = self.converter.encode(model)

        assert_that(result, equal_to(serialized_model))
        self.serializer.serialize.assert_called_once_with(mapped_model)

    def test_when_encoding_list_then_maps_each_item(self):
        model1 = Mock()
        model2 = Mock()

        self.converter.encode_list([model1, model2])

        self.mapper.for_encoding.assert_any_call(model1)
        self.mapper.for_encoding.assert_any_call(model2)

    def test_when_encoding_list_then_serializes_mapped_items(self):
        model1 = Mock()
        model2 = Mock()

        mapped_model1 = Mock()
        mapped_model2 = Mock()

        def mock_mapper(item):
            if item == model1:
                return mapped_model1
            if item == model2:
                return mapped_model2

        self.mapper.for_encoding.side_effect = mock_mapper
        serialized_models = self.serializer.serialize_list.return_value

        result = self.converter.encode_list([model1, model2], total=5)

        assert_that(result, equal_to(serialized_models))
        self.serializer.serialize_list.assert_called_once_with([mapped_model1, mapped_model2], total=5)

    def test_when_decoding_then_parses_request_using_parser(self):
        request = Mock()

        self.converter.decode(request)

        self.parser.parse.assert_called_once_with(request)

    def test_when_decoding_then_maps_parsed_request(self):
        request = Mock()

        parsed_request = self.parser.parse.return_value

        self.converter.decode(request)

        self.mapper.for_decoding.assert_called_once_with(parsed_request)

    def test_when_decoding_then_builds_model_using_mapping(self):
        request = Mock()
        expected_model = self.builder.create.return_value

        result = self.converter.decode(request)

        assert_that(result, equal_to(expected_model))
        self.builder.create.assert_called_once_with(self.mapper.for_decoding.return_value)

    def test_when_updating_then_request_parsed(self):
        request = Mock()
        model = Mock()

        self.converter.update(request, model)

        self.parser.parse.assert_called_once_with(request)

    def test_when_updating_then_request_mapped(self):
        request = Mock()
        model = Mock()
        parsed_request = self.parser.parse.return_value

        self.converter.update(request, model)

        self.mapper.for_decoding.assert_called_with(parsed_request)

    def test_when_updating_then_updates_using_mapped_request(self):
        request = Mock()
        model = Mock()
        mapped_request = self.mapper.for_decoding.return_value

        self.converter.update(request, model)

        self.builder.update.assert_called_once_with(model, mapped_request)


class TestDocumentMapper(unittest.TestCase):

    def setUp(self):
        self.document = Mock(Document)
        self.document.field_names.return_value = ('field1', 'field2', 'newname')

        self.mapper = DocumentMapper(self.document, {'oldname': 'newname'})

    def test_given_document_when_encoding_then_maps_model_using_fields_in_document(self):
        model = Mock()
        model.field1 = u'value1'
        model.field2 = u'value2'
        model.field3 = u'value3'

        result = self.mapper.for_encoding(model)

        assert_that(result, has_entries({u'field1': u'value1', u'field2': u'value2'}))

    def test_given_document_when_decoding_then_maps_dict_using_fields_in_document(self):
        mapping = {u'field1': u'value1',
                   u'field2': u'value2',
                   u'field3': u'value3'}

        result = self.mapper.for_decoding(mapping)

        assert_that(result, has_entries({u'field1': u'value1', u'field2': u'value2'}))

    def test_given_document_when_decoding_then_ignores_fields_not_in_mapping(self):
        mapping = {u'field1': u'value1',
                   u'whackyfield': u'whackyvalue'}

        result = self.mapper.for_decoding(mapping)

        assert_that(result, has_entries({u'field1': u'value1'}))

    def test_given_document_when_decoding_then_renames_fields_in_mapping(self):
        mapping = {u'oldname': u'value'}

        result = self.mapper.for_decoding(mapping)

        assert_that(result, has_entries({u'newname': u'value'}))


class TestDocumentParser(unittest.TestCase):

    def test_given_document_when_parsing_then_calls_document_parser(self):
        request = Mock()

        document = Mock(DocumentProxy)
        parsed_request = document.parse.return_value

        parser = DocumentParser(document)

        result = parser.parse(request)

        assert_that(result, equal_to(parsed_request))


class TestRequestParser(unittest.TestCase):

    def test_given_document_when_parsing_then_parses_data_from_post_and_get(self):
        request = Mock()
        request.view_args = {'line_id': 2, 'extrafield': 'extravalue'}

        document = Mock(DocumentProxy)
        document.field_names.return_value = ('user_id', 'line_id')
        document.parse.return_value = {'user_id': 1}

        parser = RequestParser(document)

        result = parser.parse(request)

        expected_entries = {'user_id': 1, 'line_id': 2}
        assert_that(result, has_entries(expected_entries))
        document.parse.assert_called_once_with(request)


@patch('flask.helpers.url_for')
class TestLinkGenerator(unittest.TestCase):

    def setUp(self):
        self.generator = LinkGenerator('users')

    def test_given_mapping_then_generates_link(self, url_for):
        url_for.side_effect = lambda r, resource_id, _external: 'http://localhost/{}/{}'.format(r.split('.')[0], resource_id)

        mapping = {'id': 1}
        expected_link = {'rel': 'users', 'href': 'http://localhost/users/1'}

        result = self.generator.generate(mapping)

        assert_that(result, has_entries(expected_link))


class TestResourceSerializer(unittest.TestCase):

    def test_given_mapping_then_generates_links(self):
        generator = Mock(LinkGenerator)
        serializer = ResourceSerializer([generator])

        user_link = {'rel': 'users', 'href': 'http://localhost/users/1'}
        generator.generate.return_value = user_link

        mapping = {'user_id': 1, 'line_id': 2}

        result = serializer.serialize(mapping)

        decoded_result = json.loads(result)

        assert_that(decoded_result, has_entries(mapping))
        assert_that(decoded_result['links'], has_item(user_link))

    def test_given_resource_id_is_none_then_does_not_add_link(self):
        generator = Mock(LinkGenerator)
        serializer = ResourceSerializer([generator])

        generator.can_generate.return_value = False
        mapping = {'user_id': None}

        result = serializer.serialize(mapping)

        decoded_result = json.loads(result)

        assert_that(decoded_result, has_entries(mapping))
        assert_that(decoded_result['links'], contains())

    def test_given_list_of_items_then_adds_total(self):
        generator = Mock(LinkGenerator)
        serializer = ResourceSerializer(generator)
        mapping = Mock()

        item = {'id': 1,
                'links': [{'rel': 'resources',
                           'href': 'http://localhost/resources/1'}]}

        with patch.object(serializer, '_map_item') as mock_serialize:
            mock_serialize.return_value = item
            result = serializer.serialize_list([mapping])

        expected_entries = {'total': 1,
                            'items': [item]}

        decoded_result = json.loads(result)
        assert_that(decoded_result, has_entries(expected_entries))

    def test_given_list_of_items_with_additional_total_then_replaces_total(self):
        generator = Mock(LinkGenerator)
        serializer = ResourceSerializer(generator)

        mapping = Mock()

        item = {'id': 1,
                'links': [{'rel': 'resources',
                           'href': 'http://localhost/resources/1'}]}

        with patch.object(serializer, '_map_item') as mock_serialize:
            mock_serialize.return_value = item
            result = serializer.serialize_list([mapping], total=5)

        expected_entries = {'total': 5,
                            'items': [item]}

        decoded_result = json.loads(result)
        assert_that(decoded_result, has_entries(expected_entries))


class TestModelBuilder(unittest.TestCase):

    def setUp(self):
        self.model_class = Mock()
        self.document = Mock(Document)
        self.builder = ModelBuilder(self.document, self.model_class)

    def test_when_creating_then_validates_mapping(self):
        mapping = {'foo': 'bar'}

        self.builder.create(mapping)

        self.document.validate.assert_called_once_with(mapping)

    def test_when_creating_then_passes_mapping_to_class(self):
        mapping = {'foo': 'bar'}

        result = self.builder.create(mapping)

        assert_that(result, equal_to(self.model_class.return_value))
        self.model_class.assert_called_once_with(foo='bar')

    def test_when_updating_then_validates_mapping(self):
        mapping = {'foo': 'bar'}
        model = Mock()

        self.builder.update(model, mapping)

        self.document.validate.assert_called_once_with(mapping)

    def test_when_updating_then_applies_mapping_to_model(self):
        mapping = {'foo': 'bar'}
        model = Mock()

        self.builder.update(model, mapping)

        assert_that(model.foo, equal_to('bar'))
