# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from xivo.caller_id import parse_caller_id
from xivo_dao.helpers.exception import InputError

from ..service import (
    OUTGOING_CALLER_ID_MAX_LENGTH,
    CallerID,
    UserCallerIDDefaultService,
    format_caller_id,
)


class TestFormatCallerID(unittest.TestCase):
    def test_with_name(self):
        self.assertEqual(
            format_caller_id('+14185551234', 'Acme Corp'), '"Acme Corp" <+14185551234>'
        )

    def test_without_name(self):
        self.assertEqual(format_caller_id('+14185551234'), '+14185551234')

    def test_quotes_are_stripped_from_the_name(self):
        self.assertEqual(
            format_caller_id('+14185551234', 'Ac"me'), '"Acme" <+14185551234>'
        )

    def test_round_trip_with_name(self):
        stored = format_caller_id('+14185551234', 'Acme Corp')
        self.assertEqual(parse_caller_id(stored), ('Acme Corp', '+14185551234'))

    def test_round_trip_without_name(self):
        stored = format_caller_id('+14185551234')
        self.assertEqual(parse_caller_id(stored), ('+14185551234', '+14185551234'))

    def test_name_is_dropped_when_the_pair_would_not_fit_the_column(self):
        # a phone number's caller_id_name is allowed 256 characters, the column
        # holding the composed value only 80
        result = format_caller_id('+14185551234', 'N' * 256)

        self.assertEqual(result, '+14185551234')
        self.assertLessEqual(len(result), OUTGOING_CALLER_ID_MAX_LENGTH)

    def test_name_is_kept_when_the_pair_just_fits(self):
        number = '+14185551234'
        # two quotes, a space and two angle brackets around the number
        name = 'N' * (OUTGOING_CALLER_ID_MAX_LENGTH - len(number) - 5)

        result = format_caller_id(number, name)

        self.assertEqual(len(result), OUTGOING_CALLER_ID_MAX_LENGTH)
        self.assertTrue(result.startswith(f'"{name}"'))


class BaseDefaultServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.callerid_service = Mock()
        self.user_dao = Mock()
        self.notifier = Mock()
        self.service = UserCallerIDDefaultService(
            self.callerid_service, self.user_dao, self.notifier
        )
        self.available = [
            CallerID(type='main', number='+14185551234', caller_id_name='Acme Corp'),
            CallerID(type='associated', number='4185559999'),
            CallerID(type='anonymous'),
        ]
        self.callerid_service.search.return_value = (
            len(self.available),
            self.available,
        )

    def a_user(self, outgoing_caller_id=''):
        return SimpleNamespace(
            id=1,
            uuid='user-uuid',
            tenant_uuid='tenant-uuid',
            outgoing_caller_id=outgoing_caller_id,
        )


class TestGetDefault(BaseDefaultServiceTestCase):
    def test_never_set_reads_as_default(self):
        # wazo-agid treats it as `default`
        result = self.service.get(self.a_user(''))
        self.assertEqual(result, CallerID(type='default'))

    def test_none_reads_as_default(self):
        result = self.service.get(self.a_user(None))
        self.assertEqual(result, CallerID(type='default'))

    def test_default_token(self):
        result = self.service.get(self.a_user('default'))
        self.assertEqual(result, CallerID(type='default'))

    def test_anonymous_token(self):
        result = self.service.get(self.a_user('anonymous'))
        self.assertEqual(result.type, 'anonymous')

    def test_stored_number_resolves_its_type_from_the_available_list(self):
        result = self.service.get(self.a_user('"Acme Corp" <+14185551234>'))
        self.assertEqual(result.type, 'main')
        self.assertEqual(result.number, '+14185551234')
        self.assertEqual(result.caller_id_name, 'Acme Corp')

    def test_bare_stored_number_resolves(self):
        result = self.service.get(self.a_user('+14185551234'))
        self.assertEqual(
            result,
            CallerID(type='main', number='+14185551234', caller_id_name='Acme Corp'),
        )

    def test_stored_name_is_not_reported_for_a_listed_number(self):
        # the name is configured on the phone number
        result = self.service.get(self.a_user('"Old Name" <+14185551234>'))
        self.assertEqual(result.caller_id_name, 'Acme Corp')

    def test_stored_unquoted_name_resolves(self):
        # the user API and the dialplan both accept an unquoted name
        result = self.service.get(self.a_user('Hursule <4185559999>'))
        self.assertEqual(
            result,
            CallerID(type='associated', number='4185559999', caller_id_name=''),
        )

    def test_bare_number_no_longer_available_reads_as_custom(self):
        result = self.service.get(self.a_user('+14180000000'))
        self.assertEqual(
            result,
            CallerID(
                type='custom', number='+14180000000', caller_id_name='+14180000000'
            ),
        )

    def test_number_without_a_name_resolves(self):
        for stored in ('"" <+14185551234>', '<+14185551234>'):
            result = self.service.get(self.a_user(stored))
            self.assertEqual(
                result,
                CallerID(
                    type='main', number='+14185551234', caller_id_name='Acme Corp'
                ),
                stored,
            )

    def test_number_without_a_name_no_longer_available_has_no_name(self):
        for stored in ('"" <+14180000000>', '<+14180000000>'):
            result = self.service.get(self.a_user(stored))
            self.assertEqual(
                result, CallerID(type='custom', number='+14180000000'), stored
            )

    def test_name_with_no_number_reads_as_custom(self):
        result = self.service.get(self.a_user('Acme Corp'))
        self.assertEqual(result, CallerID(type='custom', caller_id_name='Acme Corp'))

    def test_number_no_longer_available_reads_as_custom(self):
        result = self.service.get(self.a_user('"Gone" <+14180000000>'))
        self.assertEqual(result.type, 'custom')
        self.assertEqual(result.number, '+14180000000')


class TestEditDefault(BaseDefaultServiceTestCase):
    def test_default_stores_the_token(self):
        user = self.a_user()

        self.service.edit(user, CallerID(type='default'))

        self.assertEqual(user.outgoing_caller_id, 'default')
        self.user_dao.edit.assert_called_once_with(user)
        self.notifier.edited.assert_called_once_with(user)

    def test_anonymous_stores_the_token(self):
        user = self.a_user()

        self.service.edit(user, CallerID(type='anonymous'))

        self.assertEqual(user.outgoing_caller_id, 'anonymous')

    def test_available_number_is_stored_with_its_name(self):
        user = self.a_user()

        result = self.service.edit(user, CallerID(type='main', number='+14185551234'))

        self.assertEqual(user.outgoing_caller_id, '"Acme Corp" <+14185551234>')
        self.assertEqual(result.type, 'main')

    def test_listed_number_phonenumbers_cannot_parse_is_accepted(self):
        self.available.append(CallerID(type='shared', number='+55'))
        self.callerid_service.search.return_value = (
            len(self.available),
            self.available,
        )
        user = self.a_user()

        self.service.edit(user, CallerID(type='shared', number='+55'))

        self.assertEqual(user.outgoing_caller_id, '+55')

    def test_number_is_stored_as_listed(self):
        # wazo-agid formats it for the trunk when placing the call
        user = self.a_user()

        self.service.edit(user, CallerID(type='associated', number='4185559999'))

        self.assertEqual(user.outgoing_caller_id, '4185559999')

    def test_number_matching_semantically_is_stored_as_listed(self):
        # the caller sends E164, the available entry is national
        user = self.a_user()

        self.service.edit(user, CallerID(type='associated', number='+14185559999'))

        self.assertEqual(user.outgoing_caller_id, '4185559999')

    def test_number_too_long_for_the_column_is_rejected(self):
        long_number = '+' + '1' * 100
        self.available.append(CallerID(type='shared', number=long_number))
        self.callerid_service.search.return_value = (
            len(self.available),
            self.available,
        )
        user = self.a_user()

        with self.assertRaises(InputError):
            self.service.edit(user, CallerID(type='shared', number=long_number))

        self.user_dao.edit.assert_not_called()

    def test_number_not_available_is_rejected(self):
        user = self.a_user()

        with self.assertRaises(InputError):
            self.service.edit(user, CallerID(type='shared', number='+14180000000'))

        self.user_dao.edit.assert_not_called()
        self.notifier.edited.assert_not_called()

    def test_anonymous_entry_cannot_be_selected_by_number(self):
        user = self.a_user()

        with self.assertRaises(InputError):
            self.service.edit(user, CallerID(type='shared', number=''))
