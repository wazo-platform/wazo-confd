import unittest

from ..service import same_phone_number


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
