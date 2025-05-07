# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from hamcrest import assert_that, calling, equal_to, raises
from marshmallow import ValidationError

from wazo_confd.helpers.mallow import AsteriskSection, StrictBoolean


class TestStrictBolean(unittest.TestCase):
    def test_that_strict_boolean_raise_error(self):
        strict = StrictBoolean()._deserialize
        self.assertRaises(ValidationError, strict, '1', None, None)

    def test_that_strict_boolean_pass(self):
        strict = StrictBoolean()._deserialize
        self.assertEqual(strict(True, None, None), True)


class TestAsteriskSection(unittest.TestCase):
    def setUp(self):
        self.validator = AsteriskSection()

    def test_valid_section_names(self):
        values = ['default', 'abc-def_013.Z']
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
            assert_that(
                calling(self.validator).with_args(value), raises(ValidationError)
            )
