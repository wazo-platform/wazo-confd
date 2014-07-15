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

BASE_URL = "/1.1/lines_sip"


class TestLineSIPActions(TestResources):

    def setUp(self):
        super(TestLineSIPActions, self).setUp()
        self.line = self.build_line(id=1,
                                    protocol="sip",
                                    name='username',
                                    context='default',
                                    provisioning_extension='123456',
                                    device_slot=1,
                                    username='username',
                                    secret="secret",
                                    callerid='"John Doe" <1000>')

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
            'context': line.context,
            'device_slot': line.device_slot,
            'provisioning_extension': line.provisioning_extension,
            'username': line.username,
            'secret': line.secret,
            'callerid': line.callerid,
            'links': [{
                'href': 'http://localhost/1.1/lines_sip/%d' % line.id,
                'rel': 'lines_sip'
            }]
        }

        return item

    @patch('xivo_dao.data_handler.line.services.find_all_by_protocol')
    def test_list_lines_with_no_lines(self, mock_line_services_find_all_by_protocol):
        mock_line_services_find_all_by_protocol.return_value = []

        expected_result = {'total': 0, 'items': []}

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        mock_line_services_find_all_by_protocol.assert_called_once_with('sip')

    @patch('xivo_dao.data_handler.line.services.find_all_by_protocol')
    def test_list_lines_with_two_lines(self, mock_line_services_find_all_by_protocol):
        line1 = self.build_line(id=1)
        line2 = self.build_line(id=2)
        mock_line_services_find_all_by_protocol.return_value = [line1, line2]

        expected_result = {
            'total': 2,
            'items': [self.build_item(line1),
                      self.build_item(line2)]
        }

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        mock_line_services_find_all_by_protocol.assert_called_once_with('sip')

    @patch('xivo_dao.data_handler.line.services.get')
    def test_get(self, mock_line_services_get):
        mock_line_services_get.return_value = self.line

        expected_result = self.build_item(self.line)

        result = self.app.get("%s/%d" % (BASE_URL, self.line.id))

        self.assert_response_for_get(result, expected_result)
        mock_line_services_get.assert_called_with(self.line.id)

    @patch('xivo_dao.data_handler.line.services.create')
    def test_create(self, mock_line_services_create):
        mock_line_services_create.return_value = self.line

        expected_result = self.build_item(self.line)

        created_line = LineSIP(context=self.line.context,
                               name=self.line.username,
                               provisioning_extension=self.line.provisioning_extension,
                               device_slot=self.line.device_slot,
                               username=self.line.username)

        data = {
            'context': self.line.context,
            'provisioning_extension': self.line.provisioning_extension,
            'device_slot': self.line.device_slot,
            'username': self.line.username,
        }

        result = self.app.post(BASE_URL, data=self._serialize_encode(data))

        self.assert_response_for_create(result, expected_result)
        mock_line_services_create.assert_called_once_with(created_line)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.edit')
    def test_edit(self, mock_line_services_edit, mock_line_services_get):
        mock_line_services_get.return_value = self.line

        updated_line = self.build_line(id=1,
                                       protocol='sip',
                                       name='toto',
                                       context='default',
                                       provisioning_extension='123456',
                                       device_slot=1,
                                       username='toto',
                                       secret='secret',
                                       callerid='"John Doe" <1000>')

        data = {'username': 'toto'}

        result = self.app.put("%s/%d" % (BASE_URL, self.line.id), data=self._serialize_encode(data))

        self.assert_response_for_update(result)
        mock_line_services_get.assert_called_once_with(self.line.id)
        mock_line_services_edit.assert_called_once_with(updated_line)

    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.line.services.delete')
    def test_delete(self, mock_line_services_delete, mock_line_services_get):
        mock_line_services_get.return_value = self.line

        result = self.app.delete("%s/%s" % (BASE_URL, self.line.id))

        self.assert_response_for_delete(result)
        mock_line_services_get.assert_called_once_with(self.line.id)
        mock_line_services_delete.assert_called_with(self.line)
