# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from hamcrest import assert_that, equal_to
from marshmallow import ValidationError

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean

from ..schema import UserSchema


class _MobileFallbackSchema(BaseSchema):
    mobile_fallback_enabled = StrictBoolean()


class TestSchema(unittest.TestCase):
    def test_flatten(self):
        user_1, user_2, user_3, user_4, user_5 = Mock(), Mock(), Mock(), Mock(), Mock()
        data_to_flatten = [
            user_1,
            [[user_2, user_3]],
            [[[user_4, [[user_5]]]]],
            [],
            [[]],
        ]
        result = list(UserSchema._flatten(data_to_flatten))
        assert_that(result, equal_to([user_1, user_2, user_3, user_4, user_5]))


class TestMobileFallbackEnabledField(unittest.TestCase):
    def setUp(self):
        self.schema = _MobileFallbackSchema(handle_error=False)

    def test_load_true(self):
        result = self.schema.load({'mobile_fallback_enabled': True})
        assert_that(result['mobile_fallback_enabled'], equal_to(True))

    def test_load_false(self):
        result = self.schema.load({'mobile_fallback_enabled': False})
        assert_that(result['mobile_fallback_enabled'], equal_to(False))

    def test_load_string_rejects(self):
        self.assertRaises(
            ValidationError, self.schema.load, {'mobile_fallback_enabled': 'true'}
        )

    def test_load_integer_rejects(self):
        self.assertRaises(
            ValidationError, self.schema.load, {'mobile_fallback_enabled': 1}
        )
