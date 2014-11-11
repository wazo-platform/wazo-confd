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
# along with this program.  If not, see <http://www.gnu.org/licenses/>S

import unittest
import json

from mock import Mock, patch
from hamcrest import assert_that, equal_to, has_entries, instance_of, has_items, has_entry

from xivo_confd.helpers.converter import Converter, Mapper, Serializer, Parser
from xivo_confd.helpers.converter import DocumentMapper, DocumentParser, JsonSerializer, AssociationParser
from xivo_confd.helpers.mooltiparse.document import Document, DocumentProxy
from xivo_confd.helpers.mooltiparse.field import Field
from xivo_confd.helpers.mooltiparse.types import Unicode


class TestConverter(unittest.TestCase):

    def setUp(self):
        self.mapper = Mock(Mapper)
        self.serializer = Mock(Serializer)
        self.parser = Mock(Parser)
        self.model = Mock()

        self.converter = Converter(mapper=self.mapper,
                                   serializer=self.serializer,
                                   parser=self.parser,
                                   model=self.model)

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

    def test_when_decoding_then_creates_model_with_mapped_request(self):
        request = Mock()

        mapped_request = self.mapper.for_decoding.return_value
        created_model = self.model.return_value

        result = self.converter.decode(request)

        assert_that(result, equal_to(created_model))
        self.model.assert_called_once_with(mapped_request)

    def test_for_document_creates_document_converter(self):
        document = Mock()

        class Model(object):
            pass

        converter = Converter.for_document(document, Model)

        assert_that(converter.model, equal_to(Model))
        assert_that(converter.parser, instance_of(DocumentParser))
        assert_that(converter.mapper, instance_of(DocumentMapper))
        assert_that(converter.serializer, instance_of(JsonSerializer))
        assert_that(converter.serializer.resources, has_entry('models', 'id'))

    def test_for_document_replaces_resource_name(self):
        document = Mock()

        class Model(object):
            pass

        converter = Converter.for_document(document, Model, 'resource_name')

        assert_that(converter.serializer.resources, has_entry('resource_name', 'id'))

    def test_for_document_creates_association_converter(self):
        document = Mock()

        class Model(object):
            pass

        links = {'users': 'user_id', 'lines': 'line_id'}
        converter = Converter.for_association(document, Model, links)

        assert_that(converter.model, equal_to(Model))
        assert_that(converter.parser, instance_of(AssociationParser))
        assert_that(converter.mapper, instance_of(DocumentMapper))
        assert_that(converter.serializer, instance_of(JsonSerializer))
        assert_that(converter.serializer.resources, has_entries(links))


class TestDocumentMapper(unittest.TestCase):

    def setUp(self):
        self.document = Document([
            Field('field1', Unicode()),
            Field('field2', Unicode())])

        self.mapper = DocumentMapper(self.document)

    def test_given_document_when_encoding_then_maps_model_using_fields_in_document(self):
        model = Mock()
        model.field1 = 'value1'
        model.field2 = 'value2'
        model.field3 = 'value3'

        result = self.mapper.for_encoding(model)

        assert_that(result, has_entries({'field1': 'value1', 'field2': 'value2'}))

    def test_given_document_when_decoding_then_maps_dict_using_fields_in_document(self):
        mapping = {'field1': 'value1',
                   'field2': 'value2',
                   'field3': 'value3'}

        result = self.mapper.for_decoding(mapping)

        assert_that(result, has_entries({'field1': 'value1', 'field2': 'value2'}))


class TestDocumentParser(unittest.TestCase):

    def test_given_document_when_parsing_then_calls_document_parser(self):
        request = Mock()

        document = Mock(DocumentProxy)
        parsed_request = document.parse.return_value

        parser = DocumentParser(document)

        result = parser.parse(request)

        assert_that(result, equal_to(parsed_request))


class TestAssociationParser(unittest.TestCase):

    def test_given_document_when_parsing_then_parses_data_from_post_and_get(self):
        request = Mock()
        request.args = {'line_id': 2, 'extrafield': 'extravalue'}

        document = Mock(DocumentProxy)
        document.field_names.return_value = ['user_id', 'line_id']
        document.parse.return_value = {'user_id': 1}

        parser = AssociationParser(document)

        result = parser.parse(request)

        expected_entries = {'user_id': 1, 'line_id': 2}
        assert_that(result, has_entries(expected_entries))
        document.parse.assert_called_once_with(request)
        document.validate.assert_called_once_with(expected_entries)


class TestJsonSerializer(unittest.TestCase):

    def setUp(self):
        self.serializer = JsonSerializer({'resources': 'id'})

    @patch('flask.helpers.url_for')
    def test_given_mapping_then_generates_all_links(self, url_for):
        url_for.side_effect = lambda r, resource_id, _external: 'http://localhost/{}/{}'.format(r.split('.')[0], resource_id)
        serializer = JsonSerializer({'users': 'user_id', 'lines': 'line_id'})

        mapping = {'user_id': 1, 'line_id': 2}
        user_link = {'rel': 'users', 'href': 'http://localhost/users/1'}
        line_link = {'rel': 'lines', 'href': 'http://localhost/lines/2'}

        result = serializer.serialize(mapping)

        decoded_result = json.loads(result)

        assert_that(decoded_result, has_entries(mapping))
        assert_that(decoded_result['links'], has_items(user_link, line_link))

    def test_given_list_of_items_then_adds_total(self):
        mapping = Mock()

        item = {'id': 1,
                'links': [{'rel': 'resources',
                           'href': 'http://localhost/resources/1'}]}

        with patch.object(self.serializer, '_map_item') as mock_serialize:
            mock_serialize.return_value = item
            result = self.serializer.serialize_list([mapping])

        expected_entries = {'total': 1,
                            'items': [item]}

        decoded_result = json.loads(result)
        assert_that(decoded_result, has_entries(expected_entries))

    def test_given_list_of_items_with_additional_total_then_replaces_total(self):
        mapping = Mock()

        item = {'id': 1,
                'links': [{'rel': 'resources',
                           'href': 'http://localhost/resources/1'}]}

        with patch.object(self.serializer, '_map_item') as mock_serialize:
            mock_serialize.return_value = item
            result = self.serializer.serialize_list([mapping], total=5)

        expected_entries = {'total': 5,
                            'items': [item]}

        decoded_result = json.loads(result)
        assert_that(decoded_result, has_entries(expected_entries))
