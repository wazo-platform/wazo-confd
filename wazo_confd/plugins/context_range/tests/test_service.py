# Copyright 2023-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

from typing import NamedTuple
from unittest import TestCase
from hamcrest import assert_that, contains_exactly

from ..service import RangeFilter


class Range(NamedTuple):
    start: str
    end: str
    type: str = 'user'
    did_length: int | None = None


class TestListExtenFromRanges(TestCase):
    def test_multiple_ranges(self):
        ranges = [
            Range('1000', '1002'),
            Range('1005', '1007'),
        ]

        result = list(RangeFilter._list_exten_from_ranges(ranges))

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

        result = list(RangeFilter._list_exten_from_ranges(ranges))

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
            Range('00001', '00003'),
            Range('002', '005'),
            Range('0001', '0003'),
            Range('001', '003'),
            Range('0000', '0001'),
            Range('11110000', '11110005', type='incall', did_length=4),
        ]

        result = list(RangeFilter._list_exten_from_ranges(ranges))

        assert_that(
            result,
            contains_exactly(
                '001',
                '002',
                '003',
                '004',
                '005',
                '0000',
                '0001',
                '0002',
                '0003',
                '0004',
                '0005',
                '00001',
                '00002',
                '00003',
            ),
        )

    def test_incall_ranges(self):
        did_length = 4
        ranges = [
            Range('12345670000', '12345670010', 'incall', did_length),
            Range('12345680000', '12345680005', 'incall', did_length),
            Range('12345680006', '12345680010', 'incall', did_length),
        ]

        result = list(RangeFilter._list_exten_from_ranges(ranges))

        assert_that(
            result,
            contains_exactly(
                '0000',
                '0001',
                '0002',
                '0003',
                '0004',
                '0005',
                '0006',
                '0007',
                '0008',
                '0009',
                '0010',
            ),
        )

    def test_overlapping_ranges(self):
        ranges = [
            Range('000', '005'),
            Range('1000', '1005'),
            Range('1005', '1007'),
            Range('1000', '1010'),
        ]

        result = list(RangeFilter._list_exten_from_ranges(ranges))

        assert_that(
            result,
            contains_exactly(
                '000',
                '001',
                '002',
                '003',
                '004',
                '005',
                '1000',
                '1001',
                '1002',
                '1003',
                '1004',
                '1005',
                '1006',
                '1007',
                '1008',
                '1009',
                '1010',
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

        result = list(RangeFilter._ranges_from_extens(extens))

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

        result = list(RangeFilter._ranges_from_extens(extens))

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

        result = list(RangeFilter._ranges_from_extens(extens))

        assert_that(
            result,
            contains_exactly(
                {'start': '001', 'end': '003'},
                {'start': '0001', 'end': '0003'},
                {'start': '00001', 'end': '00003'},
            ),
        )
