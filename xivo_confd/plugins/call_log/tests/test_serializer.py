# -*- coding: UTF-8 -*-
# Copyright (C) 2012-2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from hamcrest import assert_that, equal_to
import textwrap
from unittest import TestCase
from xivo_confd.plugins.call_log import serializer
from xivo_confd.plugins.call_log.serializer import CSV_HEADERS


class TestCallLogsSerializer(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_encode_list(self):
        call_log_1 = {
            'Call Date': '01/30/2013 00:00:00',
            'Caller': 'source1 (1001)',
            'Called': '2001',
            'Period': '1',
            'user Field': ''
        }

        call_log_2 = {
            'Call Date': '01/31/2013 00:00:00',
            'Caller': u'soùrce2 (1002)',
            'Called': '2002',
            'Period': '2',
            'user Field': 'userfield'
        }
        call_logs = [call_log_1, call_log_2]
        expected_result = textwrap.dedent('''\
            %s\r
            01/30/2013 00:00:00,source1 (1001),2001,1,\r
            01/31/2013 00:00:00,soùrce2 (1002),2002,2,userfield\r
            ''' % ','.join(CSV_HEADERS))

        result = serializer.encode_list(call_logs)

        assert_that(result, equal_to(expected_result))
