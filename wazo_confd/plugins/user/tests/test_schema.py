# Copyright 2019-2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from unittest.mock import Mock

from hamcrest import assert_that, equal_to
from marshmallow import ValidationError

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean

from ..schema import UserLinePresenceSchema, UserSchema


class _MobileFallbackSchema(BaseSchema):
    mobile_fallback_enabled = StrictBoolean()


class TestUserLinePresenceSchema(unittest.TestCase):
    def setUp(self):
        self.schema = UserLinePresenceSchema()

    def test_dump_lines_and_dnd_service(self):
        user = Mock(
            uuid='abcd-uuid',
            tenant_uuid='tenant-uuid',
            dnd_enabled=True,
            lines=[{'id': 1, 'name': 'line1', 'protocol': 'sip'}],
        )

        result = self.schema.dump(user)

        assert_that(
            result,
            equal_to(
                {
                    'uuid': 'abcd-uuid',
                    'tenant_uuid': 'tenant-uuid',
                    'lines': [{'id': 1, 'name': 'line1', 'protocol': 'sip'}],
                    'services': {'dnd': {'enabled': True}},
                }
            ),
        )

    def test_dump_without_line_and_dnd_disabled(self):
        user = Mock(
            uuid='abcd-uuid',
            tenant_uuid='tenant-uuid',
            dnd_enabled=False,
            lines=[],
        )

        result = self.schema.dump(user)

        assert_that(
            result,
            equal_to(
                {
                    'uuid': 'abcd-uuid',
                    'tenant_uuid': 'tenant-uuid',
                    'lines': [],
                    'services': {'dnd': {'enabled': False}},
                }
            ),
        )


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
