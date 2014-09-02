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
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.line.model import Line
from xivo_confd.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.utils.search import SearchResult

BASE_URL = "1.1/devices"


class TestDeviceActions(TestResources):

    def setUp(self):
        super(TestDeviceActions, self).setUp()
        self.device = Device(id='1234567890abcdefghij1234567890ab',
                             ip='10.0.0.1',
                             mac='00:11:22:33:44:55',
                             plugin='zero')

    def build_item(self, device):
        links = [{'href': 'http://localhost/1.1/devices/%s' % device.id,
                  'rel': 'devices'}]

        item = {'id': device.id,
                'ip': device.ip,
                'mac': device.mac,
                'sn': device.sn,
                'plugin': device.plugin,
                'vendor': device.vendor,
                'model': device.model,
                'version': device.version,
                'description': device.description,
                'status': device.status,
                'options': device.options,
                'template_id': device.template_id,
                'links': links}

        return item

    @patch('xivo_dao.data_handler.device.services.get')
    def test_get(self, device_services_get):
        device_services_get.return_value = self.device

        expected_result = self.build_item(self.device)

        result = self.app.get("%s/%s" % (BASE_URL, self.device.id))

        self.assert_response_for_get(result, expected_result)
        device_services_get.assert_called_once_with(self.device.id)

    @patch('xivo_dao.data_handler.device.services.search')
    def test_list_no_devices(self, device_search):
        device_search.return_value = SearchResult(total=0, items=[])

        expected_result = {'total': 0, 'items': []}

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        device_search.assert_called_once_with()

    @patch('xivo_dao.data_handler.device.services.search')
    def test_list_devices_with_two_devices(self, device_search):
        device1 = Device(id='abcdefghijklmnopqrstuvwxyz123456',
                         ip='10.0.0.1',
                         mac='00:11:22:33:44:55')
        device2 = Device(id='1234567890abcdefghij1234567890abc',
                         ip='10.0.0.2',
                         mac='00:11:22:33:44:56')

        device_search.return_value = SearchResult(total=2,
                                                  items=[device1, device2])

        expected_result = {
            'total': 2,
            'items': [self.build_item(device1),
                      self.build_item(device2)]
        }

        result = self.app.get(BASE_URL)

        self.assert_response_for_list(result, expected_result)
        device_search.assert_called_once_with()

    @patch('xivo_dao.data_handler.device.services.search')
    def test_search_devices_with_parameters(self, device_search):
        device_search.return_value = SearchResult(total=0, items=[])

        expected_result = {'total': 0, 'items': []}

        search_parameters = {
            'search': 'search',
            'skip': 1,
            'limit': 2,
            'order': 'ip',
            'direction': 'asc'
        }

        query_url = "search=search&skip=1&limit=2&order=ip&direction=asc"
        result = self.app.get("%s?%s" % (BASE_URL, query_url))

        self.assert_response_for_list(result, expected_result)
        device_search.assert_called_once_with(**search_parameters)

    @patch('xivo_dao.data_handler.device.services.create')
    def test_create(self, device_services_create):
        device_services_create.return_value = self.device

        new_device = Device(mac=self.device.mac,
                            ip=self.device.ip,
                            plugin=self.device.plugin)

        request_body = {'mac': self.device.mac,
                        'ip': self.device.ip,
                        'plugin': self.device.plugin}

        expected_result = self.build_item(self.device)

        result = self.app.post(BASE_URL, data=self._serialize_encode(request_body))

        self.assert_response_for_create(result, expected_result)
        device_services_create.assert_called_once_with(new_device)

    @patch('xivo_dao.data_handler.device.services.get')
    @patch('xivo_dao.data_handler.device.services.delete')
    def test_delete(self, mock_device_services_delete, mock_device_services_get):
        mock_device_services_get.return_value = self.device

        result = self.app.delete("%s/%s" % (BASE_URL, self.device.id))

        self.assert_response_for_delete(result)
        mock_device_services_get.assert_called_once_with(self.device.id)
        mock_device_services_delete.assert_called_with(self.device)

    @patch('xivo_dao.data_handler.device.services.synchronize')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_synchronize(self, device_services_get, device_services_synchronize):
        device_services_get.return_value = self.device
        expected_status_code = 204

        result = self.app.get("%s/%s/synchronize" % (BASE_URL, self.device.id))

        assert_that(result.status_code, equal_to(expected_status_code))
        device_services_synchronize.assert_called_once_with(self.device)

    @patch('xivo_dao.data_handler.device.services.reset_to_autoprov')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_autoprov(self, device_services_get, device_services_reset_to_autoprov):
        device_services_get.return_value = self.device
        expected_status_code = 204

        result = self.app.get("%s/%s/autoprov" % (BASE_URL, self.device.id))

        assert_that(result.status_code, equal_to(expected_status_code))
        device_services_reset_to_autoprov.assert_called_once_with(self.device)

    @patch('xivo_dao.data_handler.device.services.get')
    @patch('xivo_dao.data_handler.device.services.edit')
    def test_edit(self, device_services_edit, device_services_get):
        device_services_get.return_value = self.device

        updated_device = Device(id=self.device.id,
                                ip='192.168.0.1',
                                mac='55:44:33:22:11:00',
                                plugin=self.device.plugin)

        request_body = {
            'ip': updated_device.ip,
            'mac': updated_device.mac
        }

        result = self.app.put("%s/%s" % (BASE_URL, self.device.id),
                              data=self._serialize_encode(request_body))

        self.assert_response_for_update(result)
        device_services_get.assert_called_once_with(self.device.id)
        device_services_edit.assert_called_once_with(updated_device)

    @patch('xivo_confd.helpers.request_bouncer.request')
    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.device.services.associate_line_to_device')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_associate_line(self, device_services_get, device_services_associate_line_to_device, line_services_get, request):
        device_id = '9fae3a621afd4449b006675efc6c01aa'
        line_id = 123
        expected_status_code = 204

        line = Line(id=line_id)
        device = Device(id=device_id)

        line_services_get.return_value = line
        device_services_get.return_value = device

        request.remote_addr = '127.0.0.1'

        result = self.app.get('%s/%s/associate_line/%s' % (BASE_URL, device_id, line_id))

        assert_that(result.status_code, equal_to(expected_status_code))
        device_services_associate_line_to_device.assert_called_once_with(device, line)

    @patch('xivo_confd.helpers.request_bouncer.request')
    @patch('xivo_dao.data_handler.line.services.get')
    @patch('xivo_dao.data_handler.device.services.remove_line_from_device')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_remove_line(self, device_services_get, device_services_remove_line, line_services_get, request):
        device_id = '9fae3a621afd4449b006675efc6c01aa'
        line_id = 123
        expected_status_code = 204

        line = Line(id=line_id)
        device = Device(id=device_id)

        line_services_get.return_value = line
        device_services_get.return_value = device

        request.remote_addr = '127.0.0.1'

        result = self.app.get('%s/%s/remove_line/%s' % (BASE_URL, device_id, line_id))

        assert_that(result.status_code, equal_to(expected_status_code))
        device_services_remove_line.assert_called_once_with(device, line)
