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
from hamcrest import assert_that, has_entries, has_entry
from mock import Mock
from unittest import TestCase
from xivo_restapi.resources.call_logs import mapper


class TestCallLogsMapper(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_to_api(self):
        call_log = Mock(date=datetime(2013, 1, 31),
                        source_name='source1',
                        source_exten='1001',
                        destination_name='',
                        destination_exten='2001',
                        user_field='',
                        answered=True,
                        duration=timedelta(seconds=1))

        result = mapper.to_api(call_log)

        assert_that(result, has_entries({
            'Call Date': '2013-01-31T00:00:00',
            'Caller': 'source1 (1001)',
            'Called': '2001',
            'Period': '1',
            'user Field': ''
        }))

    def test_to_api_user_field_none(self):
        call_log = Mock(duration=Mock(seconds=0, days=0), user_field=None)

        result = mapper.to_api(call_log)

        assert_that(result, has_entry('user Field', ''))
