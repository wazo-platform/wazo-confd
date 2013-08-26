# -*- coding: UTF-8 -*-
#
# Copyright (C) 2012  Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from datetime import datetime, timedelta
from hamcrest import assert_that, equal_to
from mock import Mock
import textwrap
from unittest import TestCase
from xivo_restapi.resources.call_logs import serializer
from xivo_restapi.resources.call_logs.serializer import CSV_HEADERS


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
