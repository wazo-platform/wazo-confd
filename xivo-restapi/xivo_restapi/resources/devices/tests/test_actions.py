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

from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.data_handler.device.model import Device
from xivo_dao.data_handler.line.model import Line
from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_dao.helpers.abstract_model import SearchResult

BASE_URL = "1.1/devices"


class TestDeviceActions(TestResources):

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_get(self, device_services_get, formatter):
        device_id = '1234567890abcdefghij1234567890ab'

        expected_status_code = 200
        expected_result = {
            'id': device_id,
            'links': [{
                'href': 'http://localhost/1.1/devices/%s' % device_id,
                'rel': 'devices'
            }]

        }

        device = Mock(Device)
        device_services_get.return_value = device
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        result = self.app.get("%s/%s" % (BASE_URL, device_id))

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))
        device_services_get.assert_called_once_with(device_id)
        formatter.to_api.assert_called_once_with(device)

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_no_devices(self, device_find_all):
        total = 0

        expected_status_code = 200
        expected_result = {
            'total': total,
            'items': []
        }

        devices_found = Mock(SearchResult)
        devices_found.total = total
        devices_found.items = []

        device_find_all.return_value = devices_found

        result = self.app.get(BASE_URL)

        device_find_all.assert_called_once_with()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_two_devices(self, device_find_all):
        device_id_1 = 'abcdefghijklmnopqrstuvwxyz123456'
        device_id_2 = '1234567890abcdefghij1234567890abc'
        total = 2

        device1 = Device(id=device_id_1,
                         ip='10.0.0.1',
                         mac='00:11:22:33:44:55')
        device2 = Device(id=device_id_2,
                         ip='10.0.0.2',
                         mac='00:11:22:33:44:56')

        expected_status_code = 200
        expected_result = {
            'total': total,
            'items': [
                {
                    'id': device_id_1,
                    'ip': device1.ip,
                    'mac': device1.mac,
                    'links': [{
                        'href': 'http://localhost/1.1/devices/%s' % device_id_1,
                        'rel': 'devices'
                    }]
                },
                {
                    'id': device_id_2,
                    'ip': device2.ip,
                    'mac': device2.mac,
                    'links': [{
                        'href': 'http://localhost/1.1/devices/%s' % device_id_2,
                        'rel': 'devices'
                    }]
                }
            ]
        }

        devices_found = Mock(SearchResult)
        devices_found.total = total
        devices_found.items = [device1, device2]

        device_find_all.return_value = devices_found

        result = self.app.get(BASE_URL)

        device_find_all.assert_called_once_with()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.devices.actions.extract_find_parameters')
    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_parameters(self, device_find_all, extract_find_parameters):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        find_parameters = {
            'search': 'search',
            'skip': 1,
            'limit': 2,
            'order': 'ip',
            'direction': 'asc'
        }

        extract_find_parameters.return_value = find_parameters

        devices_found = Mock(SearchResult)
        devices_found.total = 0
        devices_found.items = []

        device_find_all.return_value = devices_found

        query_url = "search=search&skip=1&limit=2&order=ip&direction=asc"
        result = self.app.get("%s?%s" % (BASE_URL, query_url))

        extract_find_parameters.assert_called_once_with()
        device_find_all.assert_called_once_with(**find_parameters)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.create')
    def test_create(self, device_services_create, formatter):
        device_id = 1
        mac = '00:11:22:33:44:55'
        ip = '10.0.0.1'
        plugin = 'null'

        expected_status_code = 201
        expected_result = {
            'id': device_id,
            'mac': mac,
            'ip': ip,
            'plugin': plugin,
            'links': [{
                'href': 'http://localhost/1.1/devices/%d' % device_id,
                'rel': 'devices'
            }]
        }

        data = {'mac': mac,
                'ip': ip,
                'plugin': plugin}

        data_serialized = self._serialize_encode(data)

        device = Mock(Device)
        created_device = Mock(Device)
        created_device.id = device_id
        created_device.ip = ip
        created_device.mac = mac
        created_device.plugin = plugin

        device_services_create.return_value = created_device
        formatter.to_model.return_value = device
        formatter.to_api.return_value = self._serialize_encode(expected_result)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized)
        device_services_create.assert_called_once_with(device)
        formatter.to_api.assert_called_once_with(created_device)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.get')
    @patch('xivo_dao.data_handler.device.services.delete')
    def test_delete_success(self, mock_device_services_delete, mock_device_services_get):
        expected_status_code = 204
        expected_data = ''

        device = Mock(Device)
        mock_device_services_get.return_value = device
        mock_device_services_delete.return_value = True

        result = self.app.delete("%s/1" % BASE_URL)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_data))
        mock_device_services_delete.assert_called_with(device)

    @patch('xivo_dao.data_handler.device.services.synchronize')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_synchronize(self, device_services_get, device_services_synchronize):
        device_id = '9fae3a621afd4449b006675efc6c01aa'
        expected_status_code = 204

        device = Device(id=device_id)
        device_services_get.return_value = device

        result = self.app.get("%s/%s/synchronize" % (BASE_URL, device_id))

        device_services_synchronize.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_dao.data_handler.device.services.reset_to_autoprov')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_autoprov(self, device_services_get, device_services_reset_to_autoprov):
        device_id = '9fae3a621afd4449b006675efc6c01aa'
        expected_status_code = 204

        device = Device(id=device_id)
        device_services_get.return_value = device

        result = self.app.get("%s/%s/autoprov" % (BASE_URL, device_id))

        device_services_reset_to_autoprov.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.get')
    @patch('xivo_dao.data_handler.device.services.edit')
    def test_edit(self, device_services_edit, device_services_get, formatter):
        expected_status_code = 204
        expected_data = ''

        data = {
            'ip': '10.0.0.1',
            'mac': '00:11:22:33:44:55',
        }
        data_serialized = self._serialize_encode(data)

        device = Mock(Device)
        device_services_get.return_value = device

        result = self.app.put("%s/1" % BASE_URL, data=data_serialized)

        formatter.update_model.assert_called_with(data_serialized, device)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(result.data, equal_to(expected_data))

    @patch('xivo_restapi.helpers.request_bouncer.request')
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

        device_services_associate_line_to_device.assert_called_once_with(device, line)
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_restapi.helpers.request_bouncer.request')
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

        device_services_remove_line.assert_called_once_with(device, line)
        assert_that(result.status_code, equal_to(expected_status_code))
