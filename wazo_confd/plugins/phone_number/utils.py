# Copyright 2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from collections.abc import Iterator
from dataclasses import dataclass


@dataclass(frozen=True)
class PhoneNumberRangeSpec:
    start_number: str
    end_number: str


def generate_phone_number_range(start_number: str, end_number: str) -> Iterator[str]:
    _start_number = int(start_number)
    _end_number = int(end_number)
    if not (_start_number <= _end_number):
        raise ValueError(
            f'Invalid range {start_number} - {end_number}: '
            'start number must precede end number following numerical ordering'
        )
    for number in range(_start_number, _end_number):
        # assert len(str(number)) == len(start_number)
        yield str(number)
    yield end_number
