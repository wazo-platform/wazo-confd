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
from xivo_dao.data_handler.exception import NonexistentParametersError, \
    InvalidParametersError, ElementNotExistsError
from xivo_dao.data_handler.device.model import Device, DeviceOrdering

BASE_URL = "1.1/devices"


class TestDeviceActions(TestResources):

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_no_device(self, device_services_get, formatter):
        expected_status_code = 404
        device_id = '1234567890abcdefghij1234567890ab'

        device_services_get.side_effect = ElementNotExistsError('device')

        result = self.app.get("%s/%s" % (BASE_URL, device_id))

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(formatter.call_count, equal_to(0))

    @patch('xivo_restapi.resources.devices.actions.formatter')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_get_error(self, device_services_get, formatter):
        expected_status_code = 500
        device_id = '1234567890abcdefghij1234567890ab'

        device_services_get.side_effect = Exception

        result = self.app.get("%s/%s" % (BASE_URL, device_id))

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(formatter.call_count, equal_to(0))

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
    def test_list_devices_with_error(self, device_find_all):
        expected_status_code = 500

        device_find_all.side_effect = Exception

        result = self.app.get(BASE_URL)

        device_find_all.assert_any_call()
        assert_that(result.status_code, equal_to(expected_status_code))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_no_devices(self, device_find_all):
        expected_status_code = 200
        expected_result = {
            'total': 0,
            'items': []
        }

        device_find_all.return_value = []

        result = self.app.get(BASE_URL)

        device_find_all.assert_called_once_with()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_two_devices(self, device_find_all):
        device_id_1 = 'abcdefghijklmnopqrstuvwxyz123456'
        device_id_2 = '1234567890abcdefghij1234567890abc'

        device1 = Device(id=device_id_1,
                         ip='10.0.0.1',
                         mac='00:11:22:33:44:55')
        device2 = Device(id=device_id_2,
                         ip='10.0.0.2',
                         mac='00:11:22:33:44:56')

        expected_status_code = 200
        expected_result = {
            'total': 2,
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

        device_find_all.return_value = [device1, device2]

        result = self.app.get(BASE_URL)

        device_find_all.assert_called_once_with()
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_ordered(self, device_find_all):
        device = Device(id='abcdefghijklmnopqrstuvwxyz123456',
                        ip='10.0.0.1',
                        mac='00:11:22:33:44:55')

        expected_status_code = 200
        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': device.id,
                    'ip': device.ip,
                    'mac': device.mac,
                    'links': [{
                        'href': 'http://localhost/1.1/devices/%s' % device.id,
                        'rel': 'devices'
                    }]
                }
            ]
        }

        device_find_all.return_value = [device]

        url = "%s?order=ip" % BASE_URL
        result = self.app.get(url)

        device_find_all.assert_called_once_with(order=DeviceOrdering.ip)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_ordered_with_a_direction(self, device_find_all):
        device = Device(id='abcdefghijklmnopqrstuvwxyz123456',
                        ip='10.0.0.1',
                        mac='00:11:22:33:44:55')

        expected_status_code = 200
        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': device.id,
                    'ip': device.ip,
                    'mac': device.mac,
                    'links': [{
                        'href': 'http://localhost/1.1/devices/%s' % device.id,
                        'rel': 'devices'
                    }]
                }
            ]
        }

        device_find_all.return_value = [device]

        url = "%s?order=ip&direction=desc" % BASE_URL
        result = self.app.get(url)

        device_find_all.assert_called_once_with(order=DeviceOrdering.ip, direction='desc')
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_an_invalid_limit(self, device_find_all):
        expected_status_code = 400
        expected_result = ["Invalid parameters: limit must be a positive number"]

        url = "%s?limit=-1" % BASE_URL
        result = self.app.get(url)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_a_limit(self, device_find_all):
        device = Device(id='abcdefghijklmnopqrstuvwxyz123456',
                        ip='10.0.0.1',
                        mac='00:11:22:33:44:55')

        expected_status_code = 200
        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': device.id,
                    'ip': device.ip,
                    'mac': device.mac,
                    'links': [{
                        'href': 'http://localhost/1.1/devices/%s' % device.id,
                        'rel': 'devices'
                    }]
                }
            ]
        }

        device_find_all.return_value = [device]

        url = "%s?limit=1" % BASE_URL
        result = self.app.get(url)

        device_find_all.assert_called_once_with(limit=1)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_an_invalid_skip(self, device_find_all):
        expected_status_code = 400
        expected_result = ["Invalid parameters: skip must be a positive number"]

        url = "%s?skip=-1" % BASE_URL
        result = self.app.get(url)

        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

    @patch('xivo_dao.data_handler.device.services.find_all')
    def test_list_devices_with_a_skip(self, device_find_all):
        device = Device(id='abcdefghijklmnopqrstuvwxyz123456',
                        ip='10.0.0.1',
                        mac='00:11:22:33:44:55')

        expected_status_code = 200
        expected_result = {
            'total': 1,
            'items': [
                {
                    'id': device.id,
                    'ip': device.ip,
                    'mac': device.mac,
                    'links': [{
                        'href': 'http://localhost/1.1/devices/%s' % device.id,
                        'rel': 'devices'
                    }]
                }
            ]
        }

        device_find_all.return_value = [device]

        url = "%s?skip=1" % BASE_URL
        result = self.app.get(url)

        device_find_all.assert_called_once_with(skip=1)
        assert_that(result.status_code, equal_to(expected_status_code))
        assert_that(self._serialize_decode(result.data), equal_to(expected_result))

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

    @patch('xivo_dao.data_handler.device.services.reset_to_autoprov')
    @patch('xivo_dao.data_handler.device.services.get')
    def test_autoprov_with_error(self, device_services_get, device_services_reset_to_autoprov):
        device_id = '9fae3a621afd4449b006675efc6c01aa'
        expected_status_code = 500

        device = Device(id=device_id)
        device_services_get.return_value = device
        device_services_reset_to_autoprov.side_effect = Exception

        result = self.app.get("%s/%s/autoprov" % (BASE_URL, device_id))

        device_services_reset_to_autoprov.assert_called_once_with(device)
        assert_that(result.status_code, equal_to(expected_status_code))
