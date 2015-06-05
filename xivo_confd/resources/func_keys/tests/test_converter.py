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

from __future__ import unicode_literals


import unittest

from mock import Mock, sentinel, patch
from hamcrest import assert_that, equal_to, calling, raises

from xivo_dao.helpers.exception import InputError

from xivo_confd.helpers.mooltiparse.field import Field
from xivo_confd.resources.func_keys.converter import JsonParser, \
    TemplateMapper, TemplateValidator, TemplateBuilder, \
    FuncKeyMapper, FuncKeyValidator, FuncKeyBuilder, \
    DestinationBuilder

from xivo_confd.resources.func_keys.converter import UserDestinationBuilder, \
    ConferenceDestinationBuilder, GroupDestinationBuilder, QueueDestinationBuilder, \
    PagingDestinationBuilder, BSFilterDestinationBuilder, CustomDestinationBuilder, \
    ServiceDestinationBuilder, ForwardDestinationBuilder, TransferDestinationBuilder, \
    ParkPositionDestinationBuilder, ParkingDestinationBuilder, AgentDestinationBuilder

from xivo_dao.resources.func_key.model import FuncKey
from xivo_dao.resources.func_key_template.model import FuncKeyTemplate
from xivo_dao.resources.func_key.model import UserDestination, \
    GroupDestination, QueueDestination, ConferenceDestination, \
    PagingDestination, BSFilterDestination, CustomDestination, \
    ServiceDestination, ForwardDestination, TransferDestination, \
    ParkPositionDestination, ParkingDestination, AgentDestination


class TestJsonParser(unittest.TestCase):

    def setUp(self):
        self.parser = JsonParser()

    def build_request(self, body):
        return Mock(json=body)

    def test_given_json_data_then_returns_dict(self):
        expected = {'foo': 'bar'}
        request = self.build_request(expected)

        result = self.parser.parse(request)

        assert_that(result, equal_to(expected))


class TestTemplateMapper(unittest.TestCase):

    def setUp(self):
        self.funckey_mapper = Mock(FuncKeyMapper)
        self.mapper = TemplateMapper(self.funckey_mapper)

    def test_given_json_dict_when_decoding_then_returns_dict(self):
        expected = {'name': 'foo',
                    'description': 'bar'}

        result = self.mapper.for_decoding(expected)

        assert_that(result, equal_to(expected))

    def test_given_json_dict_with_keys_when_decoding_then_converts_key_positions(self):
        body = {'name': 'foo',
                'description': 'bar',
                'keys': {'1': {'destination': 'parking'},
                         '2': {'destination': 'custom'}}}

        expected = {'name': 'foo',
                    'description': 'bar',
                    'keys': {1: {'destination': 'parking'},
                             2: {'destination': 'custom'}}}

        result = self.mapper.for_decoding(body)

        assert_that(result, equal_to(expected))

    def test_given_empty_model_when_encoding_then_returns_bare_mapping(self):
        model = FuncKeyTemplate(id=1, name='foobar')
        expected = {'id': 1,
                    'name': 'foobar',
                    'description': None,
                    'keys': {}}

        result = self.mapper.for_encoding(model)

        assert_that(result, equal_to(expected))

    def test_given_template_with_funckey_when_encoding_then_encodes_funckeys(self):
        funckey = Mock(FuncKey)
        model = FuncKeyTemplate(id=1, name='foobar',
                                keys={1: funckey})

        expected_mapping = self.funckey_mapper.for_encoding.return_value

        expected = {'id': 1,
                    'name': 'foobar',
                    'description': None,
                    'keys': {1: expected_mapping}}

        result = self.mapper.for_encoding(model)

        assert_that(result, equal_to(expected))


class TestFuncKeyMapper(unittest.TestCase):

    def setUp(self):
        self.builder = Mock(DestinationBuilder)
        self.builders = {'spam': self.builder}
        self.mapper = FuncKeyMapper(self.builders)

    def test_given_json_dict_when_decoding_then_returns_dict(self):
        expected = {'label': 'foo',
                    'blf': True,
                    'destination': {'type': 'spam'}}

        result = self.mapper.for_decoding(expected)

        assert_that(result, equal_to(expected))

    def test_given_model_when_encoding_then_encodes_funckey_and_destination(self):
        destination = Mock(type='spam')

        expected_destination = self.builder.to_mapping.return_value
        expected = {'id': sentinel.id,
                    'label': None,
                    'blf': False,
                    'destination': expected_destination}

        model = FuncKey(id=sentinel.id, destination=destination)

        result = self.mapper.for_encoding(model)

        assert_that(result, equal_to(expected))


class TestTemplateValidator(unittest.TestCase):

    def setUp(self):
        self.funckey_validator = Mock(FuncKeyValidator)
        self.validator = TemplateValidator(self.funckey_validator)

    def test_given_missing_required_fields_when_creating_then_raises_error(self):
        body = {}

        assert_that(calling(self.validator.validate).with_args(body, action='create'),
                    raises(InputError))

    def test_given_unknown_fields_when_validating_then_raises_error(self):
        body = {'name': 'foobar', 'invalid': 'invalid'}

        assert_that(calling(self.validator.validate).with_args(body),
                    raises(InputError))

    def test_given_invalid_keys_mapping_when_validating_then_raises_error(self):
        body = {'name': 'foobar',
                'keys': 'spam'}

        assert_that(calling(self.validator.validate).with_args(body),
                    raises(InputError))

    def test_given_keys_mapping_are_negative_when_validating_then_raises_error(self):
        body = {'name': 'foobar',
                'keys': {-1: 'spam'}}

        assert_that(calling(self.validator.validate).with_args(body),
                    raises(InputError))

    def test_given_mapping_when_validating_then_validates_using_funckey_validator(self):
        funckey = {'type': 'spam'}
        body = {'name': 'foobar',
                'keys': {1: funckey}}

        self.validator.validate(body)
        self.funckey_validator.validate.assert_called_once_with(funckey)


class TestFuncKeyValidator(unittest.TestCase):

    def setUp(self):
        self.builder = Mock(DestinationBuilder)
        self.validator = FuncKeyValidator({'foobar': self.builder})

    def test_given_required_fields_missing_when_creating_then_raises_error(self):
        body = {}

        assert_that(calling(self.validator.validate).with_args(body, action='create'),
                    raises(InputError))

    def test_given_destination_has_wrong_type_when_creating_then_raises_error(self):
        body = {'destination': 'invalid'}

        assert_that(calling(self.validator.validate).with_args(body),
                    raises(InputError))

    def test_given_destination_has_no_type_when_creating_then_raises_error(self):
        body = {'destination': {}}

        assert_that(calling(self.validator.validate).with_args(body),
                    raises(InputError))

    def test_given_unknown_destination_type_when_creating_then_raises_error(self):
        body = {'destination': {'type': 'invalid'}}

        assert_that(calling(self.validator.validate).with_args(body),
                    raises(InputError))

    def test_given_destination_when_validating_then_calls_destination_validator(self):
        destination = {'type': 'foobar'}
        body = {'destination': destination}

        self.validator.validate(body)

        self.builder.validate.assert_called_once_with(destination)


class TestTemplateBuilder(unittest.TestCase):

    def setUp(self):
        self.validator = Mock(TemplateValidator)
        self.funckey_builder = Mock(FuncKeyBuilder)
        self.builder = TemplateBuilder(self.validator, self.funckey_builder)

    def test_given_template_with_funckeys_when_creating_then_returns_model(self):
        expected_func_key = self.funckey_builder.create.return_value
        expected = FuncKeyTemplate(name='foobar',
                                   description=None,
                                   keys={1: expected_func_key})

        body = {'name': 'foobar',
                'keys': {1: {'destination': {'type': 'user'}}}}

        result = self.builder.create(body)

        assert_that(result, equal_to(expected))

    def test_given_template_with_complete_funckeys_when_creating_then_returns_model(self):
        expected_func_key = self.funckey_builder.create.return_value
        expected = FuncKeyTemplate(name='foobar',
                                   description='a foobar template',
                                   keys={1: expected_func_key})

        body = {'name': 'foobar',
                'description': 'a foobar template',
                'keys': {1: {'label': 'myuser',
                             'blf': True,
                             'destination': {'type': 'user'}}}}

        result = self.builder.create(body)

        assert_that(result, equal_to(expected))

    def test_given_template_when_updating_then_updates_model(self):
        model = FuncKeyTemplate(name='foobar',
                                description='a foobar template',
                                keys={})

        expected = FuncKeyTemplate(name='otherfoobar',
                                   description='another description',
                                   keys={})

        body = {'name': 'otherfoobar',
                'description': 'another description'}

        self.builder.update(model, body)

        assert_that(model, equal_to(expected))

    def test_given_funckey_when_updating_then_updates_keys(self):
        unmodified_key = Mock(FuncKey)
        original_key = Mock(FuncKey)

        model = FuncKeyTemplate(name='foobar',
                                description='a foobar template',
                                keys={1: unmodified_key,
                                      2: original_key})

        key = {'type': 'user'}
        body = {'keys': {2: key}}

        self.builder.update(model, body)

        self.funckey_builder.update.assert_called_once_with(original_key, key)


class TestDestinationBuilder(unittest.TestCase):

    def test_given_set_of_fields_then_runs_validators(self):

        field = Mock(Field)
        field.name = 'foobar'

        class TestBuilder(DestinationBuilder):

            destination = 'destination'

            fields = [field]

            def to_model(self, destination):
                pass

        builder = TestBuilder()
        builder.validate({'foobar': sentinel.foobar})

        field.validate.assert_called_once_with(sentinel.foobar)

    def test_given_destination_then_maps_fields(self):

        field = Mock(Field)
        field.name = 'foobar'

        destination = Mock()
        destination.foobar = 'spam'

        class TestBuilder(DestinationBuilder):

            destination = 'destination'

            fields = [field]

            def to_model(self, destination):
                pass

        builder = TestBuilder()
        result = builder.to_mapping(destination)

        expected = {'foobar': 'spam',
                    'type': 'destination',
                    'href': None}

        assert_that(result, equal_to(expected))


class TestUserDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = UserDestinationBuilder()

    def test_given_destination_type_user_then_returns_user_destination(self):
        dest = {'type': 'user',
                'user_id': 1}

        expected = UserDestination(user_id=1)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))

    @patch('xivo_confd.resources.func_keys.converter.url_for')
    def test_given_destination_then_generates_url(self, url_for):
        dest = UserDestination(user_id=sentinel.user_id)

        expected = url_for.return_value

        result = self.builder.url(dest)

        assert_that(result, equal_to(expected))
        url_for.assert_called_once_with('users.get', _external=True, resource_id=sentinel.user_id)


class TestGroupDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = GroupDestinationBuilder()

    def test_given_destination_type_group_then_returns_group_destination(self):
        dest = {'type': 'group',
                'group_id': 1}

        expected = GroupDestination(group_id=1)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestQueueDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = QueueDestinationBuilder()

    def test_given_destination_type_queue_then_returns_queue_destination(self):
        dest = {'type': 'queue',
                'queue_id': 1}

        expected = QueueDestination(queue_id=1)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestConferenceDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ConferenceDestinationBuilder()

    def test_given_destination_type_conference_then_returns_conference_destination(self):
        dest = {'type': 'conference',
                'conference_id': 1}

        expected = ConferenceDestination(conference_id=1)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestPagingDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = PagingDestinationBuilder()

    def test_given_destination_type_paging_then_returns_paging_destination(self):
        dest = {'type': 'paging',
                'paging_id': 1}

        expected = PagingDestination(paging_id=1)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestBSFilterDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = BSFilterDestinationBuilder()

    def test_given_destination_type_queue_then_returns_queue_destination(self):
        dest = {'type': 'bsfilter',
                'filter_member_id': 1}

        expected = BSFilterDestination(filter_member_id=1)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestCustomDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = CustomDestinationBuilder()

    def test_given_destination_type_custom_then_returns_custom_destination(self):
        dest = {'type': 'bsfilter',
                'exten': '1234567890'}

        expected = CustomDestination(exten='1234567890')

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestServiceDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ServiceDestinationBuilder()

    def test_given_destination_type_service_then_returns_service_destination(self):
        dest = {'type': 'bsfilter',
                'service': 'enablevm'}

        expected = ServiceDestination(service='enablevm')

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestForwardDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ForwardDestinationBuilder()

    def test_given_destination_type_forward_then_returns_forward_destination(self):
        dest = {'type': 'forward',
                'forward': 'noanswer',
                'exten': '1000'}

        expected = ForwardDestination(forward='noanswer',
                                      exten='1000')

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestTransferDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = TransferDestinationBuilder()

    def test_given_destination_type_transfer_then_returns_transfer_destination(self):
        dest = {'type': 'transfer',
                'transfer': 'blind'}

        expected = TransferDestination(transfer='blind')

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestParkPositionDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ParkPositionDestinationBuilder()

    def test_given_destination_type_park_position_then_returns_park_position_destination(self):
        dest = {'type': 'park_position',
                'position': 701}

        expected = ParkPositionDestination(position=701)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestParkingDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = ParkingDestinationBuilder()

    def test_given_destination_type_parking_then_returns_parking_destination(self):
        dest = {'type': 'parking'}

        expected = ParkingDestination()

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))


class TestAgentDestinationBuilder(unittest.TestCase):

    def setUp(self):
        self.builder = AgentDestinationBuilder()

    def test_given_destination_type_parking_then_returns_parking_destination(self):
        dest = {'type': 'agent',
                'action': 'login',
                'agent_id': 1234}

        expected = AgentDestination(action='login', agent_id=1234)

        result = self.builder.build(dest)

        assert_that(result, equal_to(expected))
