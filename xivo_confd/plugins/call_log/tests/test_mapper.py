# -*- coding: UTF-8 -*-
#
# Copyright 2012-2017 The Wazo Authors  (see the AUTHORS file)
#
# SPDX-License-Identifier: GPL-3.0+

from datetime import datetime
from hamcrest import assert_that, has_entries, has_entry
from mock import Mock
from unittest import TestCase
from xivo_confd.plugins.call_log import mapper


class TestCallLogsMapper(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_to_api(self):
        call_log = Mock(date=datetime(2013, 1, 31, 00, 00, 00),
                        date_answer=datetime(2013, 1, 31, 00, 00, 2),
                        date_end=datetime(2013, 1, 31, 00, 00, 5),
                        source_name='source1',
                        source_exten='1001',
                        destination_name='',
                        destination_exten='2001',
                        user_field='')

        result = mapper.to_api(call_log)

        assert_that(result, has_entries({
            'Call Date': '2013-01-31T00:00:00',
            'Caller': 'source1 (1001)',
            'Called': '2001',
            'Period': '3',
            'user Field': ''
        }))

    def test_to_api_user_field_none(self):
        call_log = Mock(date_answer=None, user_field=None)

        result = mapper.to_api(call_log)

        assert_that(result, has_entry('user Field', ''))
