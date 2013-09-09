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

from xivo_restapi.helpers.tests.test_resources import TestResources
from xivo_dao.data_handler.exception import NonexistentParametersError, InvalidParametersError
from xivo_dao.data_handler.device.model import Device

BASE_URL = "1.1/devices"


class TestDeviceActions(TestResources):

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.create')
    def test_create_nonexistent_parameters(self, device_services_create, formatter):
        expected_status_code = 400
        expected_result = ["Nonexistent parameters: template_id abcd does not exist"]

        device = Mock(Device)

        device_services_create.side_effect = NonexistentParametersError(template_id='abcd')
        formatter.to_model.return_value = device

        data = {}

        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized)
        device_services_create.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.create')
    def test_create_invalid_parameters(self, device_services_create, formatter):
        expected_status_code = 400
        expected_result = ["Invalid parameters: mac"]

        device = Mock(Device)

        device_services_create.side_effect = InvalidParametersError(["mac"])
        formatter.to_model.return_value = device

        data = {'mac': 'asdfghjk'}

        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized)
        device_services_create.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.create')
    def test_create_unknown_error(self, device_services_create, formatter):
        expected_status_code = 500

        device = Mock(Device)

        device_services_create.side_effect = Exception()
        formatter.to_model.return_value = device

        data = {'mac': '00:11:22:33:44:55', 'ip': '10.0.0.1'}

        data_serialized = self._serialize_encode(data)

        result = self.app.post(BASE_URL, data=data_serialized)

        formatter.to_model.assert_called_once_with(data_serialized)
        device_services_create.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))

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

    @patch('xivo_dao.data_handler.device.services.synchronize')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_synchronize_with_error(self, device_services_get, device_services_synchronize):
        device_id = '9fae3a621afd4449b006675efc6c01aa'
        expected_status_code = 500

        device = Device(id=device_id)
        device_services_get.return_value = device
        device_services_synchronize.side_effect = Exception

        result = self.app.get("%s/%s/synchronize" % (BASE_URL, device_id))

        device_services_synchronize.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))
