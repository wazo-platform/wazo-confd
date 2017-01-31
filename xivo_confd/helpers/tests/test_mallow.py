# -*- coding: UTF-8 -*-

# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import unittest

from mock import Mock
from hamcrest import assert_that, calling, equal_to, raises
from marshmallow import ValidationError, fields
from xivo_confd.helpers.mallow import BaseSchema, StrictBoolean, AsteriskSection


class TestStrictBolean(unittest.TestCase):

    def test_that_strict_boolean_raise_error(self):
        strict = StrictBoolean()._deserialize
        self.assertRaises(ValidationError, strict, '1', None, None)

    def test_that_strict_boolean_pass(self):
        strict = StrictBoolean()._deserialize
        self.assertEqual(strict(True, None, None), True)


class TestBaseSchema(unittest.TestCase):

    def test_that_schema_reference_unloaded_plugin_does_not_raise(self):
        class FakeSchema(BaseSchema):
            uuid = fields.String()
            unloaded = fields.Nested('UnloadedSchema')

        fake = Mock(uuid='abcd-1234', unloaded=Mock(uuid='efgh-5678'))
        data = FakeSchema().dump(fake).data
        assert_that(data, equal_to({'uuid': 'abcd-1234'}))


class TestAsteriskSection(unittest.TestCase):

    def setUp(self):
        self.validator = AsteriskSection()

    def test_valid_section_names(self):
        values = [
            'default',
            'abc-def_013.Z',
        ]
        for value in values:
            assert_that(self.validator(value), equal_to(value))

    def test_invalid_section_names(self):
        values = [
            '',
            'a' * 80,
            'foo bar',
            'foo;',
            'foo\nbar',
            'foo\n#exec /bin/rm -rf /',
            'foo]',
            '[foo',
            'general',
        ]
        for value in values:
            assert_that(calling(self.validator).with_args(value),
                        raises(ValidationError))
