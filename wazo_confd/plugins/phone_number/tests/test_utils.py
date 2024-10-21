from wazo_confd.plugins.phone_number.utils import generate_phone_number_range


import unittest


class TestGeneratePhoneNumberRange(unittest.TestCase):
    def test_singleton_range(self):
        numbers = list(generate_phone_number_range('15550000000', '15550000000'))
        assert numbers and len(numbers) == 1 and numbers[0] == '15550000000'

    def test_normal_range(self):
        start_number = '15550000000'
        end_number = '15550000999'
        numbers = list(generate_phone_number_range(start_number, end_number))

        # this generates 1000 numbers
        assert numbers and len(numbers) == 1000
        # start and end numbers are part of generated numbers
        assert numbers[0] == start_number
        assert numbers[-1] == end_number
        # common prefix
        assert all(number.startswith(start_number[:7]) for number in numbers)

    def test_invalid_range_bad_order(self):
        with self.assertRaises(ValueError):
            _ = list(generate_phone_number_range('15550000000', '15540001000'))

    def test_invalid_range_non_numerical_number(self):
        with self.assertRaises(ValueError):
            _ = list(generate_phone_number_range('1555000WAZO', '15540001000'))
