# Copyright 2021-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from unittest import TestCase

from hamcrest import assert_that, has_entries

from ..destination import UserDestinationSchema


class TestUserDestinationSchema(TestCase):
    def setUp(self):
        self.schema = UserDestinationSchema()

    def test_actionarg2_serialisation(self):
        moh_uuid = '53ff7e19-1872-4547-9bb7-bd00a20f840f'
        base_body = {'type': 'user', 'user_id': 42}
        samples = [
            ({}, ''),
            ({'moh_uuid': moh_uuid}, ';{}'.format(moh_uuid)),
            ({'ring_time': 0}, '0.0'),
            ({'ring_time': 42, 'moh_uuid': moh_uuid}, '42.0;{}'.format(moh_uuid)),
        ]
        for extra_args, expected in samples:
            body = dict(**base_body, **extra_args)
            result = self.schema.load(body)
            assert_that(result, has_entries(actionarg2=expected))
