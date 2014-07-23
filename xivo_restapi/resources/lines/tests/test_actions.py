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

from mock import patch

from xivo_dao.data_handler.line.model import LineSIP
from xivo_restapi.helpers.tests.test_resources import TestResources

BASE_URL = "/1.1/lines"


class TestLineActions(TestResources):

    def setUp(self):
        super(TestLineActions, self).setUp()
        self.line = self.build_line(id=1,
                                    protocol='sip',
                                    context='default',
                                    name='test1',
                                    provisioning_extension=123456,
                                    device_slot=1,
                                    device_id="b054de13b8b73d5683815929c20033ad")

    def build_line(self, **kwargs):
        params = {
            'id': None,
            'name': None,
            'number': None,
            'context': None,
            'protocol': None,
            'protocolid': None,
            'callerid': None,
            'device_id': None,
            'provisioning_extension': None,
            'configregistrar': None,
            'device_slot': None,
            'username': None,
            'secret': None,
        }
        params.update(kwargs)

        line = LineSIP()
        for name, value in params.iteritems():
            setattr(line, name, value)

        return line

    def build_item(self, line):
        item = {
            'id': line.id,
            'name': line.name,
            'protocol': line.protocol,
            'context': line.context,
            'device_slot': line.device_slot,
            'device_id': line.device_id,
            'provisioning_extension': line.provisioning_extension,
            'links': [{
                'href': 'http://localhost/1.1/lines/%d' % line.id,
                'rel': 'lines'
            }]
        }

        return item

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_with_no_lines(self, mock_line_services_find_all):
        mock_line_services_find_all.return_value = []

        expected_result = {'total': 0, 'items': []}

        result = self.app.get(BASE_URL)

        self.assert_response_for_get(result, expected_result)
        mock_line_services_find_all.assert_any_call()

    @patch('xivo_dao.data_handler.line.services.find_all')
    def test_list_lines_with_two_lines(self, mock_line_services_find_all):
        line1 = self.build_line(id=1, name='test1')
        line2 = self.build_line(id=2, name='test2')

        mock_line_services_find_all.return_value = [line1, line2]

        expected_result = {
            'total': 2,
            'items': [self.build_item(line1),
                      self.build_item(line2)]
        }

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        mock_line_services_find_all.assert_any_call()

    @patch('xivo_dao.data_handler.line.services.find_all_by_name')
    def test_list_lines_with_search(self, mock_line_services_find_all_by_name):
        mock_line_services_find_all_by_name.return_value = [self.line]

        search = 'bob'

        expected_result = {'total': 1, 'items': [self.build_item(self.line)]}

        result = self.app.get("%s?q=%s" % (BASE_URL, search))

        self.assert_response_for_list(result, expected_result)
        mock_line_services_find_all_by_name.assert_called_once_with(search)

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get(self, mock_line_services_get):
        mock_line_services_get.return_value = self.line

        expected_result = self.build_item(self.line)

        result = self.app.get("%s/%d" % (BASE_URL, self.line.id))

        self.assert_response_for_get(result, expected_result)
        mock_line_services_get.assert_called_with(self.line.id)
