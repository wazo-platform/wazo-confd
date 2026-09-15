# Copyright 2026 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from xivo_dao.helpers.exception import InputError

from ..service import (
    CallerID,
    CallerIDDefault,
    UserCallerIDDefaultService,
    format_caller_id,
    normalize_e164,
    parse_caller_id,
)


class TestNormalizeE164(unittest.TestCase):
    def test_national_number_with_country(self):
        self.assertEqual(normalize_e164('4185551234', 'CA'), '+14185551234')

    def test_already_e164(self):
        self.assertEqual(normalize_e164('+14185551234', 'CA'), '+14185551234')

    def test_no_country_leaves_national_number_alone(self):
        self.assertEqual(normalize_e164('4185551234', None), '4185551234')

    def test_unparseable_is_returned_unchanged(self):
        self.assertEqual(normalize_e164('not-a-number', 'CA'), 'not-a-number')

    def test_invalid_number_is_returned_unchanged(self):
        self.assertEqual(normalize_e164('123', 'CA'), '123')


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
        self.assertEqual(parse_caller_id(stored), ('+14185551234', 'Acme Corp'))

    def test_round_trip_without_name(self):
        stored = format_caller_id('+14185551234')
        self.assertEqual(parse_caller_id(stored), ('+14185551234', ''))


class BaseDefaultServiceTestCase(unittest.TestCase):
    def setUp(self):
        self.callerid_service = Mock()
        self.user_dao = Mock()
        self.tenant_dao = Mock()
        self.notifier = Mock()
        self.service = UserCallerIDDefaultService(
            self.callerid_service, self.user_dao, self.tenant_dao, self.notifier
        )
        self.tenant_dao.find.return_value = SimpleNamespace(country='CA')
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
    def test_unset_reads_as_default(self):
        result = self.service.get(self.a_user(''))
        self.assertEqual(result, CallerIDDefault(type='default'))

    def test_none_reads_as_default(self):
        result = self.service.get(self.a_user(None))
        self.assertEqual(result, CallerIDDefault(type='default'))

    def test_default_token(self):
        result = self.service.get(self.a_user('default'))
        self.assertEqual(result.type, 'default')

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
        self.assertEqual(result.type, 'main')
        self.assertEqual(result.caller_id_name, 'Acme Corp')

    def test_number_no_longer_available_reads_as_custom(self):
        result = self.service.get(self.a_user('"Gone" <+14180000000>'))
        self.assertEqual(result.type, 'custom')
        self.assertEqual(result.number, '+14180000000')


class TestEditDefault(BaseDefaultServiceTestCase):
    def test_default_stores_the_token(self):
        user = self.a_user()

        self.service.edit(user, CallerIDDefault(type='default'))

        self.assertEqual(user.outgoing_caller_id, 'default')
        self.user_dao.edit.assert_called_once_with(user)
        self.notifier.edited.assert_called_once_with(user)

    def test_anonymous_stores_the_token(self):
        user = self.a_user()

        self.service.edit(user, CallerIDDefault(type='anonymous'))

        self.assertEqual(user.outgoing_caller_id, 'anonymous')

    def test_available_number_is_stored_with_its_name(self):
        user = self.a_user()

        result = self.service.edit(
            user, CallerIDDefault(type='main', number='+14185551234')
        )

        self.assertEqual(user.outgoing_caller_id, '"Acme Corp" <+14185551234>')
        self.assertEqual(result.type, 'main')

    def test_national_number_is_normalized_to_e164(self):
        user = self.a_user()

        self.service.edit(user, CallerIDDefault(type='associated', number='4185559999'))

        self.assertEqual(user.outgoing_caller_id, '+14185559999')

    def test_number_matching_semantically_is_accepted(self):
        # the caller sends E164, the available entry is national
        user = self.a_user()

        self.service.edit(
            user, CallerIDDefault(type='associated', number='+14185559999')
        )

        self.assertEqual(user.outgoing_caller_id, '+14185559999')

    def test_number_not_available_is_rejected(self):
        user = self.a_user()

        with self.assertRaises(InputError):
            self.service.edit(
                user, CallerIDDefault(type='shared', number='+14180000000')
            )

        self.user_dao.edit.assert_not_called()
        self.notifier.edited.assert_not_called()

    def test_anonymous_entry_cannot_be_selected_by_number(self):
        user = self.a_user()

        with self.assertRaises(InputError):
            self.service.edit(user, CallerIDDefault(type='shared', number=''))

    def test_tenant_without_country_stores_the_number_as_is(self):
        self.tenant_dao.find.return_value = SimpleNamespace(country=None)
        user = self.a_user()

        self.service.edit(user, CallerIDDefault(type='associated', number='4185559999'))

        self.assertEqual(user.outgoing_caller_id, '4185559999')
