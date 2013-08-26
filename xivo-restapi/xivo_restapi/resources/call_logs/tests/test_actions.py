# -*- coding: UTF-8 -*-

# Copyright (C) 2013 Avencall
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

import textwrap
from datetime import datetime, timedelta
from mock import Mock, patch
from hamcrest import assert_that, equal_to, has_entry
from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_restapi.resources.call_logs.serializer import CSV_HEADERS

BASE_URL = "/1.1/call_logs"


class TestCallLogActions(TestResources):

    @patch('xivo_dao.data_handler.call_log.services.find_all')
    def test_list_call_logs_with_no_call_logs(self, mock_call_log_services_find_all):
        expected_status_code = 200
        expected_result = ','.join(CSV_HEADERS) + '\r\n'

        mock_call_log_services_find_all.return_value = []

        result = self.app.get(BASE_URL)

        mock_call_log_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_result))

    @patch('xivo_dao.data_handler.call_log.services.find_all')
    def test_list_call_logs_with_call_logs(self, mock_call_log_services_find_all):
        expected_status_code = 200
        expected_result = textwrap.dedent('''\
            %s\r
            01/01/2013 00:00:00,source1 (1001),2001,1,\r
            01/02/2013 00:00:00,soùrce2 (1002),2002,2,userfield\r
            ''' % ','.join(CSV_HEADERS))
        call_log_1 = Mock(date=datetime(2013, 1, 1),
                          source_name='source1',
                          source_exten='1001',
                          destination_name='',
                          destination_exten='2001',
                          user_field='',
                          answered=True,
                          duration=timedelta(seconds=1))

        call_log_2 = Mock(date=datetime(2013, 1, 2),
                          source_name=u'soùrce2',
                          source_exten='1002',
                          destination_name='',
                          destination_exten='2002',
                          user_field='userfield',
                          answered=False,
                          duration=timedelta(seconds=2))

        mock_call_log_services_find_all.return_value = [call_log_1, call_log_2]

        result = self.app.get(BASE_URL)

        mock_call_log_services_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_result))
        assert_that(result.headers, has_entry('Content-disposition',
                                              'attachment;filename=xivo-call-logs.csv'))
