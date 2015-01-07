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

from datetime import datetime
import re

from hamcrest import assert_that, equal_to, has_entries
from mock import Mock, patch

from xivo_confd.helpers.tests.test_resources import TestResources
from xivo_confd.resources.call_logs.serializer import CSV_HEADERS
from xivo_dao.data_handler.call_log.model import CallLog


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
    @patch('xivo_confd.resources.call_logs.mapper.to_api')
    @patch('xivo_confd.resources.call_logs.serializer.encode_list')
    def test_list_call_logs_with_call_logs(self, serialize_encode, mapper_to_api, mock_call_log_services_find_all):
        expected_status_code = 200
        call_log_1, call_log_2 = mock_call_log_services_find_all.return_value = [Mock(CallLog), Mock(CallLog)]
        mapped_1, mapped_2 = mapper_to_api.side_effect = [Mock(), Mock()]
        serialized_data = serialize_encode.return_value = 'field1,field2\r\nvalue1,value2\r\n'

        result = self.app.get(BASE_URL)

        mock_call_log_services_find_all.assert_called_once_with()
        mapper_to_api.assert_any_call(call_log_1)
        mapper_to_api.assert_any_call(call_log_2)
        assert_that(mapper_to_api.call_count, equal_to(2))
        serialize_encode.assert_called_once_with([mapped_1, mapped_2])
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(serialized_data))
        assert_that(result.headers, has_entries({
            'Content-disposition': 'attachment;filename=xivo-call-logs.csv',
        }))

    @patch('xivo_dao.data_handler.call_log.services.find_all_in_period')
    @patch('xivo_confd.resources.call_logs.mapper.to_api')
    @patch('xivo_confd.resources.call_logs.serializer.encode_list')
    def test_list_call_logs_with_call_logs_interval(self, serialize_encode, mapper_to_api, mock_call_log_services_find_period):
        expected_status_code = 200
        expected_start, expected_end = datetime(2013, 1, 1), datetime(2013, 1, 2)
        call_log_1, call_log_2 = mock_call_log_services_find_period.return_value = [Mock(CallLog), Mock(CallLog)]
        mapped_1, mapped_2 = mapper_to_api.side_effect = [Mock(), Mock()]
        serialized_data = serialize_encode.return_value = 'field1,field2\r\nvalue1,value2\r\n'

        result = self.app.get(BASE_URL + '?start_date=2013-01-01T00:00:00&end_date=2013-01-02T00:00:00')

        mock_call_log_services_find_period.assert_called_once_with(expected_start, expected_end)
        mapper_to_api.assert_any_call(call_log_1)
        mapper_to_api.assert_any_call(call_log_2)
        assert_that(mapper_to_api.call_count, equal_to(2))
        serialize_encode.assert_called_once_with([mapped_1, mapped_2])
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(serialized_data))
        assert_that(result.headers, has_entries({
            'Content-disposition': 'attachment;filename=xivo-call-logs.csv',
        }))

    def test_list_call_logs_with_wrongly_formatted_date(self):
        result = self.app.get(BASE_URL + '?start_date=20AB-12-14')

        self.assert_error(result, re.compile('start_date'))
