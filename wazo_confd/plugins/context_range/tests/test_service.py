# Copyright 2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections import namedtuple
from unittest import TestCase
from hamcrest import assert_that, contains_exactly

from ..service import _list_exten_from_ranges, _ranges_from_extens


Range = namedtuple('Range', ['start', 'end'])


class TestListExtenFromRanges(TestCase):
    def test_multiple_ranges(self):
        ranges = [
            Range('1000', '1002'),
            Range('1005', '1007'),
        ]

        result = list(_list_exten_from_ranges(ranges))

        assert_that(
            result,
            contains_exactly(
                '1000',
                '1001',
                '1002',
                '1005',
                '1006',
                '1007',
            ),
        )

    def test_range_with_leading_zeros(self):
        ranges = [
            Range('0001', '0003'),
        ]

        result = list(_list_exten_from_ranges(ranges))

        assert_that(
            result,
            contains_exactly(
                '0001',
                '0002',
                '0003',
            ),
        )

    def test_range_mixed_length(self):
        ranges = [
            Range('001', '003'),
            Range('0001', '0003'),
            Range('00001', '00003'),
        ]

        result = list(_list_exten_from_ranges(ranges))

        assert_that(
            result,
            contains_exactly(
                '001',
                '002',
                '003',
                '0001',
                '0002',
                '0003',
                '00001',
                '00002',
                '00003',
            ),
        )


class TestRangesFromExtens(TestCase):
    def test_multiple_ranges(self):
        extens = [
            '1000',
            '1001',
            '1002',
            '1005',
            '1006',
            '1007',
        ]

        result = list(_ranges_from_extens(extens))

        assert_that(
            result,
            contains_exactly(
                {'start': '1000', 'end': '1002'},
                {'start': '1005', 'end': '1007'},
            ),
        )

    def test_leading_zeros(self):
        extens = [
            '0001',
            '0002',
            '0003',
        ]

        result = list(_ranges_from_extens(extens))

        assert_that(
            result,
            contains_exactly(
                {'start': '0001', 'end': '0003'},
            ),
        )

    def test_mixed_length(self):
        extens = [
            '001',
            '002',
            '003',
            '0001',
            '0002',
            '0003',
            '00001',
            '00002',
            '00003',
        ]

        result = list(_ranges_from_extens(extens))

        assert_that(
            result,
            contains_exactly(
                {'start': '001', 'end': '003'},
                {'start': '0001', 'end': '0003'},
                {'start': '00001', 'end': '00003'},
            ),
        )
