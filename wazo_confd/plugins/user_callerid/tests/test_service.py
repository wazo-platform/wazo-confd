import unittest
from types import SimpleNamespace
from unittest.mock import Mock

from ..service import UserCallerIDService, same_phone_number


class TestSamePhoneNumber(unittest.TestCase):
    def test_exact(self):
        numbers = ['1234567890', '11234567890', '+11234567890' '4567890', '911']
        for number in numbers:
            self.assertTrue(same_phone_number(number, number), number)

    def test_actually_different(self):
        number1 = '11234567890'
        number2 = '11234567891'
        self.assertFalse(same_phone_number(number1, number2), (number1, number2))

    def test_different_country(self):
        number1 = '11234567890'
        number2 = '21234567890'
        self.assertFalse(same_phone_number(number1, number2), (number1, number2))

    def test_different_country_one_e164(self):
        number1 = '+11234567890'
        number2 = '21234567890'
        self.assertFalse(same_phone_number(number1, number2), (number1, number2))


class TestUserCallerIDService(unittest.TestCase):
    def setUp(self):
        self.user_dao = Mock()
        self.incall_dao = Mock()
        self.phone_number_dao = Mock()
        self.service = UserCallerIDService(
            self.user_dao, self.incall_dao, self.phone_number_dao
        )
        self.user_dao.list_outgoing_callerid_associated.return_value = []
        self.phone_number_dao.find_by.return_value = None
        self.phone_number_dao.find_all_by.return_value = []

    def test_main_callerid_has_caller_id_name(self):
        self.phone_number_dao.find_by.return_value = SimpleNamespace(
            number='5551234', caller_id_name='Acme Corp'
        )

        total, callerids = self.service.search(1, 'tenant-uuid', {})

        main = [c for c in callerids if c.type == 'main'][0]
        self.assertEqual(main.caller_id_name, 'Acme Corp')

    def test_main_callerid_without_caller_id_name(self):
        self.phone_number_dao.find_by.return_value = SimpleNamespace(
            number='5551234', caller_id_name=None
        )

        total, callerids = self.service.search(1, 'tenant-uuid', {})

        main = [c for c in callerids if c.type == 'main'][0]
        self.assertEqual(main.caller_id_name, '')

    def test_shared_callerid_has_caller_id_name(self):
        self.phone_number_dao.find_all_by.return_value = [
            SimpleNamespace(number='5559876', caller_id_name='Support Line')
        ]

        total, callerids = self.service.search(1, 'tenant-uuid', {})

        shared = [c for c in callerids if c.type == 'shared'][0]
        self.assertEqual(shared.caller_id_name, 'Support Line')

    def test_anonymous_callerid_has_empty_caller_id_name(self):
        total, callerids = self.service.search(1, 'tenant-uuid', {})

        anon = [c for c in callerids if c.type == 'anonymous'][0]
        self.assertEqual(anon.caller_id_name, '')

    def test_associated_callerid_has_empty_caller_id_name(self):
        self.user_dao.list_outgoing_callerid_associated.return_value = [
            SimpleNamespace(type='associated', number='5555678')
        ]

        total, callerids = self.service.search(1, 'tenant-uuid', {})

        associated = [c for c in callerids if c.type == 'associated'][0]
        self.assertEqual(associated.caller_id_name, '')
