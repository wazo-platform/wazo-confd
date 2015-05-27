# -*- coding: UTF-8 -*-

# Copyright (C) 2013-2015 Avencall
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
import json

from mock import patch, Mock, sentinel
from hamcrest import assert_that, equal_to, calling, raises

from xivo_confd.resources.func_keys.converter import JsonParser, JsonMapper, \
    TemplateBuilder, DestinationBuilder
from xivo_confd.resources.func_keys.model import FuncKeyTemplate
from xivo_dao.helpers.exception import InputError


class TestJsonParser(unittest.TestCase):

    def setUp(self):
        self.parser = JsonParser()

    def build_request(self, body):
        encoded = json.dumps(body)
        return Mock(body=encoded)

    def test_given_json_data_then_returns_dict(self):
        expected = {'foo': 'bar'}
        request = self.build_request(expected)

        result = self.parser.parse(request)

        assert_that(result, equal_to(expected))


class TestJsonMapper(unittest.TestCase):

    def setUp(self):
        self.mapper = JsonMapper()

    def test_given_json_dict_when_encoding_then_returns_dict(self):
        expected = {'foo': 'bar'}

        result = self.mapper.for_encoding(expected)

        assert_that(result, equal_to(expected))

    def test_given_json_dict_when_decoding_then_returns_dict(self):
        expected = {'foo': 'bar'}

        result = self.mapper.for_decoding(expected)

        assert_that(result, equal_to(expected))



class TestTemplateBuilder(unittest.TestCase):

    def setUp(self):
        self.dest_builder = Mock(DestinationBuilder)
        self.dest_builders = {'user': self.dest_builder}
        self.builder = TemplateBuilder(self.dest_builders)

    def test_given_missing_required_fields_when_creating_then_raises_error(self):
        body = {}

        assert_that(calling(self.builder.create).with_args(body),
                    raises(InputError))

    def test_given_unknown_fields_when_creating_then_raises_error(self):
        body = {'name': 'foobar', 'invalid': 'invalid'}

        assert_that(calling(self.builder.create).with_args(body),
                    raises(InputError))

    def test_given_invalid_keys_mapping_when_creating_then_raises_error(self):
        body = {'name': 'foobar',
                'keys': 'spam'}

        assert_that(calling(self.builder.create).with_args(body),
                    raises(InputError))

    def test_given_keys_mapping_are_not_numbers_when_creating_then_raises_error(self):
        body = {'name': 'foobar',
                'keys': {'1': {'type': 'user',
                               'user_id': 1}}}

        assert_that(calling(self.builder.create).with_args(body),
                    raises(InputError))

    def test_given_destination_has_no_type_when_creating_then_raises_error(self):
        body = {'name': 'foobar',
                'keys': {1: {'foo': 'bar'}}}

        assert_that(calling(self.builder.create).with_args(body),
                    raises(InputError))

    def test_given_unknown_destination_type_when_creating_then_raises_error(self):
        body = {'name': 'foobar',
                'keys': {1: {'type': 'foobar'}}}

        assert_that(calling(self.builder.create).with_args(body),
                    raises(InputError))

    def test_given_template_with_funckeys_when_creating_then_returns_model(self):
        expected_destination = self.dest_builder.build.return_value

        expected = FuncKeyTemplate(name='foobar',
                                   description='a foobar template',
                                   keys={1: expected_destination})

        body = {'name': 'foobar',
                'description': 'a foobar template',
                'keys': {1: {'type': 'user',
                             'user_id': sentinel.user_id}}}

        result = self.builder.create(body)

        assert_that(result, equal_to(expected))
