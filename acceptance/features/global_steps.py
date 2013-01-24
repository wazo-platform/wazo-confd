# -*- coding: UTF-8 -*-
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
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA..

from lettuce import step
from xivo_recording.recording_config import RecordingConfig
status = None

@step(u'When I send a "([^"]*)" request to "([^"]*)"')
def when_i_send_a_group1_request_to_group2(step, method, url):
    connection = RecordingConfig.getWSConnection()
    headers = RecordingConfig.CTI_REST_DEFAULT_CONTENT_TYPE
    connection.request(method, url, None, headers)
    global status
    status = connection.getresponse().status


@step(u'Then I get a response with status code "([^"]*)"')
def then_i_get_a_response_with_status_code_group1(step, status_code):
    global status
    print status, " ", type(status)
    assert status == int(status_code), "Expected status was " + status_code + \
                    ", actual was " + str(status)
