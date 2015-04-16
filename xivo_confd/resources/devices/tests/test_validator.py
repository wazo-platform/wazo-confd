# -*- coding: utf-8 -*-

# Copyright (C) 2013-2014 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

import unittest
from mock import patch, Mock
from hamcrest import assert_that, equal_to

from xivo_dao.resources.device import validator
from xivo_dao.resources.exception import InputError
from xivo_dao.resources.exception import ResourceError
from xivo_dao.resources.device.model import Device


class TestDeviceValidator(unittest.TestCase):

    @patch('xivo_dao.resources.device.dao.mac_exists')
    def test_validate_create_mac_already_exists(self, dao_mac_exists):
        device = Device(mac='00:11:22:33:44:55')

        dao_mac_exists.return_value = True

        self.assertRaises(ResourceError, validator.validate_create, device)

        dao_mac_exists.assert_called_once_with(device.mac)

    def test_validate_create_invalid_ip(self):
        device = {
            'id': '02aff2a361004aaf8a8a686a48dc980d',
            'ip': '10.9.0.5156'
        }
        device = Device(**device)

        self.assertRaises(InputError, validator.validate_create, device)

    def test_validate_create_ip_over_255(self):
        device = {
            'id': '02aff2a361004aaf8a8a686a48dc980d',
            'ip': '10.259.0.0'
        }
        device = Device(**device)

        self.assertRaises(InputError, validator.validate_create, device)

    def test_validate_create_invalid_mac(self):
        device = {
            'id': '02aff2a361004aaf8a8a686a48dc980d',
            'mac': 'ZA:22:33:44:55:66'
        }
        device = Device(**device)

        self.assertRaises(InputError, validator.validate_create, device)

    def test_validate_create_invalid_options_type(self):
        device = Device()
        device.options = 'foobar'

        self.assertRaises(InputError, validator.validate_create, device)

    def test_validate_create_invalid_switchboard_option_type(self):
        device = Device()
        device.options = {'switchboard': 42}

        self.assertRaises(InputError, validator.validate_create, device)

    @patch('xivo_dao.resources.device.dao.mac_exists', Mock(return_value=False))
    @patch('xivo_dao.resources.device.dao.plugin_exists')
    def test_validate_create_plugin_does_not_exist(self, dao_plugin_exists):
        device = {
            'plugin': 'superduperplugin',
        }
        device = Device(**device)

        dao_plugin_exists.return_value = False

        self.assertRaises(InputError, validator.validate_create, device)

    @patch('xivo_dao.resources.device.dao.mac_exists', Mock(return_value=False))
    @patch('xivo_dao.resources.device.dao.plugin_exists', Mock(return_value=True))
    @patch('xivo_dao.resources.device.dao.template_id_exists')
    def test_validate_create_template_does_not_exist(self, dao_template_id_exists):
        device = {
            'template_id': 'mysuperdupertemplate',
        }
        device = Device(**device)

        dao_template_id_exists.return_value = False

        self.assertRaises(InputError, validator.validate_create, device)

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.plugin_exists')
    @patch('xivo_dao.resources.device.dao.template_id_exists')
    def test_validate_create(self, template_id_exists, plugin_exists, mac_exists):
        template_id_exists.return_value = True
        plugin_exists.return_value = True
        mac_exists.return_value = False

        device = {
            'mac': '00:11:22:33:44:55',
            'ip': '10.40.0.210',
            'template_id': 'defaultconfigdevice',
            'plugin': 'null',
            'options': {'switchboard': True},
        }

        device = Device(**device)

        validator.validate_create(device)

        template_id_exists.assert_called_once_with(device.template_id)
        plugin_exists.assert_called_once_with(device.plugin)
        mac_exists.assert_called_once_with(device.mac)

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.plugin_exists')
    @patch('xivo_dao.resources.device.dao.template_id_exists')
    @patch('xivo_dao.resources.device.dao.find')
    def test_validate_edit(self, dao_find, template_id_exists, plugin_exists, mac_exists):
        device_found = Mock(Device)
        device_found.mac = '00:11:22:33:44:54'

        dao_find.return_value = device_found
        template_id_exists.return_value = True
        plugin_exists.return_value = True
        mac_exists.return_value = False

        device_id = '123abc'

        device = {
            'id': device_id,
            'mac': '00:11:22:33:44:55',
            'ip': '10.0.0.1',
            'template_id': 'defaultconfigdevice',
            'plugin': 'null',
        }

        device = Device(**device)

        validator.validate_edit(device)

        dao_find.assert_called_once_with(device_id)
        template_id_exists.assert_called_once_with(device.template_id)
        plugin_exists.assert_called_once_with(device.plugin)
        mac_exists.assert_called_once_with(device.mac)

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.find')
    def test_validate_same_mac(self, dao_find, mac_exists):
        mac = '00:11:22:33:44:55'
        device_id = '123abc'

        device_found = Mock(Device)
        device_found.mac = mac
        dao_find.return_value = device_found

        device = {
            'id': device_id,
            'mac': '00:11:22:33:44:55',
        }

        device = Device(**device)

        validator.validate_edit(device)

        dao_find.assert_called_once_with(device_id)
        assert_that(mac_exists.call_count, equal_to(0))

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.find')
    def test_validate_different_mac(self, dao_find, mac_exists):
        mac_found = '00:11:22:33:44:55'
        new_mac = '00:11:22:33:44:56'
        device_id = '123abc'

        device_found = Mock(Device)
        device_found.mac = mac_found

        dao_find.return_value = device_found
        mac_exists.return_value = False

        device = {
            'id': device_id,
            'mac': new_mac,
        }

        device = Device(**device)

        validator.validate_edit(device)

        dao_find.assert_called_once_with(device_id)
        mac_exists.assert_called_once_with(new_mac)

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.find')
    def test_validate_source_has_no_mac(self, dao_find, mac_exists):
        new_mac = '00:11:22:33:44:56'
        device_id = '123abc'

        device_found = Mock(Device, mac=None)
        dao_find.return_value = device_found

        device = {
            'id': device_id,
            'mac': new_mac,
        }

        device = Device(**device)

        validator.validate_edit(device)

        dao_find.assert_called_once_with(device_id)
        assert_that(mac_exists.call_count, equal_to(0))

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.find')
    def test_validate_edited_device_has_no_mac(self, dao_find, mac_exists):
        mac_found = '00:11:22:33:44:56'
        device_id = '123abc'

        device_found = Mock(Device)
        device_found.mac = mac_found
        dao_find.return_value = device_found

        device = {
            'id': device_id,
        }

        device = Device(**device)

        validator.validate_edit(device)

        dao_find.assert_called_once_with(device_id)
        assert_that(mac_exists.call_count, equal_to(0))

    @patch('xivo_dao.resources.device.dao.mac_exists')
    @patch('xivo_dao.resources.device.dao.find')
    def test_validate_new_mac_already_exists(self, dao_find, mac_exists):
        mac_found = '00:11:22:33:44:56'
        new_mac = '00:11:22:33:44:57'
        device_id = '123abc'

        device_found = Mock(Device)
        device_found.mac = mac_found
        dao_find.return_value = device_found

        mac_exists.return_value = True

        device = {
            'id': device_id,
            'mac': new_mac,
        }

        device = Device(**device)

        self.assertRaises(ResourceError, validator.validate_edit, device)
        dao_find.assert_called_once_with(device_id)
        mac_exists.assert_called_once_with(new_mac)

    @patch('xivo_dao.resources.line.dao.find_all_by_device_id')
    def test_validate_delete_ok(self, find_all_by_device_id):
        device = Mock(id='abc123')
        find_all_by_device_id.return_value = []

        validator.validate_delete(device)

        find_all_by_device_id.assert_called_once_with(device.id)

    @patch('xivo_dao.resources.line.dao.find_all_by_device_id')
    def test_validate_delete_linked_to_line(self, find_all_by_device_id):
        device = Mock(id='abc123')
        find_all_by_device_id.return_value = [Mock(id=1)]

        self.assertRaises(ResourceError, validator.validate_delete, device)

        find_all_by_device_id.assert_called_once_with(device.id)
