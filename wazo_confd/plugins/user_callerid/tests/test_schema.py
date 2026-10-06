# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest

from marshmallow import ValidationError

from ..schema import UserCallerIDDefaultSchema
from ..service import CallerID


class TestUserCallerIDDefaultSchemaLoad(unittest.TestCase):
    def setUp(self):
        # handle_error=False so validation raises instead of aborting with a 400
        self.schema = UserCallerIDDefaultSchema(handle_error=False)

    def test_default_needs_no_number(self):
        result = self.schema.load({'type': 'default'})
        self.assertEqual(result, CallerID(type='default'))

    def test_anonymous_needs_no_number(self):
        result = self.schema.load({'type': 'anonymous'})
        self.assertEqual(result, CallerID(type='anonymous'))

    def test_number_type_carries_its_number(self):
        result = self.schema.load({'type': 'shared', 'number': '+14185551234'})
        self.assertEqual(result, CallerID(type='shared', number='+14185551234'))

    def test_number_type_without_number_is_rejected(self):
        for type_ in ('main', 'associated', 'shared'):
            with self.assertRaises(ValidationError, msg=type_):
                self.schema.load({'type': type_})

    def test_type_is_required(self):
        with self.assertRaises(ValidationError):
            self.schema.load({'number': '+14185551234'})

    def test_custom_cannot_be_set(self):
        with self.assertRaises(ValidationError):
            self.schema.load({'type': 'custom', 'number': '+14185551234'})

    def test_unknown_type_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.schema.load({'type': 'nonsense'})

    def test_non_numeric_number_is_rejected(self):
        with self.assertRaises(ValidationError):
            self.schema.load({'type': 'shared', 'number': 'drop table users'})


class TestUserCallerIDDefaultSchemaDump(unittest.TestCase):
    def setUp(self):
        self.schema = UserCallerIDDefaultSchema()

    def test_default_omits_number(self):
        result = self.schema.dump(CallerID(type='default'))
        self.assertEqual(result, {'type': 'default'})

    def test_anonymous_omits_number(self):
        result = self.schema.dump(CallerID(type='anonymous'))
        self.assertEqual(result, {'type': 'anonymous'})

    def test_number_type_is_dumped_in_full(self):
        result = self.schema.dump(
            CallerID(type='main', number='+14185551234', caller_id_name='Acme Corp')
        )
        self.assertEqual(
            result,
            {
                'type': 'main',
                'number': '+14185551234',
                'caller_id_name': 'Acme Corp',
            },
        )

    def test_custom_is_reported(self):
        result = self.schema.dump(CallerID(type='custom', number='+14180000000'))
        self.assertEqual(result['type'], 'custom')
        self.assertEqual(result['number'], '+14180000000')
