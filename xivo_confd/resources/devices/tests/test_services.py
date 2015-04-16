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
from hamcrest import assert_that, equal_to, is_not, has_item

from mock import patch, Mock
from urllib2 import URLError
from xivo_dao.resources.utils.search import SearchResult
from xivo_dao.resources.device import services as device_services
from xivo_dao.resources.device.model import Device
from xivo_dao.resources.extension.model import Extension
from xivo_dao.resources.line.model import LineSIP, LineSCCP
from xivo_dao.resources.line_extension.model import LineExtension
from xivo_dao.resources.exception import DataError
from xivo_dao.resources.exception import InputError
from xivo_dao.helpers import provd_connector


class TestDeviceServices(unittest.TestCase):

    def setUp(self):
        self.device_id = 'ad0a12fd5f244ae68a3c626789203698'
        self.provd_config_manager = Mock(provd_connector.config_manager)
        self.provd_device_manager = Mock(provd_connector.device_manager)

    @patch('xivo_dao.resources.device.dao.get')
    def test_get(self, dao_get):
        device = Mock(Device)
        dao_get.return_value = device

        result = device_services.get(self.device_id)

        self.assertEquals(result, device)
        dao_get.assert_called_once_with(self.device_id)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search(self, device_dao_search):
        expected = Mock(SearchResult)

        device_dao_search.return_value = expected

        result = device_services.search({})

        self.assertEquals(result, expected)
        device_dao_search.assert_called_once_with()

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_invalid_order(self, device_dao_search):
        self.assertRaises(InputError, device_services.search, {'order': 'toto'})
        self.assertEquals(device_dao_search.call_count, 0)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_valid_order(self, device_dao_search):
        expected = Mock(SearchResult)

        device_dao_search.return_value = expected

        result = device_services.search({'order': 'ip'})

        self.assertEquals(result, expected)
        device_dao_search.assert_called_once_with(order='ip')

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_invalid_direction(self, device_dao_search):
        self.assertRaises(InputError, device_services.search, {'direction': 'toto'})
        self.assertEquals(device_dao_search.call_count, 0)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_valid_direction(self, device_dao_search):
        expected = Mock(SearchResult)

        device_dao_search.return_value = expected

        result = device_services.search({'direction': 'desc'})

        self.assertEquals(result, expected)
        device_dao_search.assert_called_once_with(direction='desc')

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_invalid_limit(self, device_dao_search):
        self.assertRaises(InputError, device_services.search, {'limit': -1})
        self.assertEquals(device_dao_search.call_count, 0)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_limit_at_0(self, device_dao_search):
        self.assertRaises(InputError, device_services.search, {'limit': 0})
        self.assertEquals(device_dao_search.call_count, 0)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_valid_limit(self, device_dao_search):
        expected = Mock(SearchResult)

        device_dao_search.return_value = expected

        result = device_services.search({'limit': 1})

        self.assertEquals(result, expected)
        device_dao_search.assert_called_once_with(limit=1)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_invalid_skip(self, device_dao_search):
        self.assertRaises(InputError, device_services.search, {'skip': -1})
        self.assertEquals(device_dao_search.call_count, 0)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_skip_at_0(self, device_dao_search):
        expected = Mock(SearchResult)

        device_dao_search.return_value = expected

        result = device_services.search({'skip': 0})

        self.assertEquals(result, expected)

        device_dao_search.assert_called_once_with(skip=0)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_valid_skip(self, device_dao_search):
        expected = Mock(SearchResult)

        device_dao_search.return_value = expected

        result = device_services.search({'skip': 1})

        self.assertEquals(result, expected)
        device_dao_search.assert_called_once_with(skip=1)

    @patch('xivo_dao.resources.device.dao.search')
    def test_search_with_search(self, device_dao_search):
        search_term = 'toto'
        device = Mock(Device)

        expected = [device]

        device_dao_search.return_value = expected

        result = device_services.search({'search': search_term})

        self.assertEquals(result, expected)
        device_dao_search.assert_called_once_with(search=search_term)

    @patch('xivo_dao.resources.device.dao.create')
    @patch('xivo_dao.resources.device.notifier.created')
    def test_create_empty_device(self, notifier_created, device_dao_create):
        device = Device()
        created_device = Device(id='abcd')

        device_dao_create.return_value = created_device

        result = device_services.create(device)

        self.assertEquals(result.id, created_device.id)
        device_dao_create.assert_called_once_with(device)
        notifier_created.assert_called_once_with(result)

    @patch('xivo_dao.resources.device.notifier.created')
    @patch('xivo_dao.resources.device.dao.create')
    @patch('xivo_dao.resources.device.validator.validate_create')
    def test_create(self, validate_create, device_dao_create, notifier_created):
        expected_device = {
            'ip': '10.9.0.5',
            'mac': '00:11:22:33:44:55',
            'template_id': 'abcd1234',
            'plugin': 'superduperplugin',
            'vendor': 'Aastra',
            'model': '6531i',
        }
        device = Device(**expected_device)

        device_dao_create.return_value = Device(**expected_device)

        result = device_services.create(device)

        validate_create.assert_called_with(device)
        device_dao_create.assert_called_once_with(device)
        notifier_created.assert_called_once_with(result)
        self.assertEquals(result.mac, expected_device['mac'])
        self.assertEquals(result.ip, expected_device['ip'])
        self.assertEquals(result.template_id, expected_device['template_id'])
        self.assertEquals(result.plugin, expected_device['plugin'])
        self.assertEquals(result.vendor, expected_device['vendor'])
        self.assertEquals(result.model, expected_device['model'])

    @patch('xivo_dao.resources.device.notifier.edited')
    @patch('xivo_dao.resources.device.dao.edit')
    @patch('xivo_dao.resources.device.validator.validate_edit')
    def test_edit(self, device_validate, dao_edit, notifier_edit):
        device = Mock(Device)

        device_services.edit(device)

        device_validate.assert_called_once_with(device)
        dao_edit.assert_called_once_with(device)
        notifier_edit.assert_called_once_with(device)

    @patch('xivo_dao.resources.device.notifier.deleted')
    @patch('xivo_dao.resources.line.dao.reset_device')
    @patch('xivo_dao.resources.device.dao.delete')
    @patch('xivo_dao.resources.device.validator.validate_delete', Mock())
    def test_delete_unassociated(self, device_dao_delete, line_dao_reset_device, device_notifier_deleted):
        device = Device(id=self.device_id,
                        ip='10.0.0.1')

        device_services.delete(device)

        device_dao_delete.assert_called_once_with(device)
        line_dao_reset_device.assert_called_once_with(device.id)
        device_notifier_deleted.assert_called_once_with(device)

    @patch('xivo_dao.resources.device.services.rebuild_device_config')
    @patch('xivo_dao.resources.device.provd_converter.link_device_config')
    @patch('xivo_dao.resources.line.dao.edit')
    def test_associate_line_to_device(self, line_dao_edit, link_device_config, rebuild_device_config):
        device = Device(id=self.device_id)
        line = LineSIP()

        device_services.associate_line_to_device(device, line)

        line_dao_edit.assert_called_once_with(line)
        link_device_config.assert_called_once_with(device)
        rebuild_device_config.assert_called_once_with(device)
        self.assertEquals(line.device_id, self.device_id)

    @patch('xivo_dao.resources.device.services.build_line_for_device')
    @patch('xivo_dao.resources.line.dao.find_all_by_device_id')
    def test_rebuild_device_config(self, line_find_all_by_device_id, build_line_for_device):
        device = Device(id=self.device_id)
        line1 = LineSIP(device_id=self.device_id)
        line_find_all_by_device_id.return_value = [line1]

        device_services.rebuild_device_config(device)

        build_line_for_device.assert_called_once_with(device, line1)

    @patch('xivo_dao.resources.device.services.build_line_for_device')
    @patch('xivo_dao.resources.line.dao.find_all_by_device_id')
    def test_rebuild_device_config_provd_error(self,
                                               line_find_all_by_device_id,
                                               build_line_for_device):
        device = Device(id=self.device_id)
        line1 = LineSIP(device_id=self.device_id)
        line_find_all_by_device_id.return_value = [line1]
        build_line_for_device.side_effect = URLError('urlerror')

        self.assertRaises(DataError, device_services.rebuild_device_config, device)

        build_line_for_device.assert_called_once_with(device, line1)

    @patch('xivo_dao.resources.device.services.build_line_for_device')
    @patch('xivo_dao.resources.line.dao.find_all_by_device_id')
    def test_rebuild_device_config_2_lines_same_device(self, line_find_all_by_device_id, build_line_for_device):
        device = Device(id=self.device_id)
        line1 = LineSIP(device_id=self.device_id)
        line2 = LineSIP(device_id=self.device_id)
        line_find_all_by_device_id.return_value = [line1, line2]

        device_services.rebuild_device_config(device)

        build_line_for_device.assert_called_with(device, line1)
        build_line_for_device.assert_called_with(device, line2)

    @patch('xivo_dao.resources.device.services.build_line_for_device')
    @patch('xivo_dao.resources.line.dao.find_all_by_device_id')
    def test_rebuild_device_config_no_result(self, line_find_all_by_device_id, build_line_for_device):
        device = Device(id=self.device_id)
        line_find_all_by_device_id.return_value = []

        device_services.rebuild_device_config(device)

        self.assertEquals(build_line_for_device.call_count, 0)

    @patch('xivo_dao.resources.extension.dao.get')
    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_build_line_for_device_with_a_sip_line(self, config_manager, find_by_line_id, extension_dao_get):
        username = '1234'
        secret = 'password'
        exten = '1250'
        context = 'default'
        display_name = 'Francis Dagobert'
        callerid = '"%s" <%s>' % (display_name, exten)
        proxy_ip = '10.39.5.1'
        registrar_ip = proxy_ip
        configregistrar = 'default'

        line = LineSIP(id=1,
                       device_slot=1,
                       context=context,
                       username=username,
                       name=username,
                       secret=secret,
                       callerid=callerid,
                       configregistrar=configregistrar)
        device = Device(id=self.device_id)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip)
        config_manager().get.side_effect = (provd_base_config, config_registrar_dict)
        find_by_line_id.return_value = LineExtension(line_id=line.id,
                                                     extension_id=3)
        extension_dao_get.return_value = Extension(exten=exten,
                                                   context=context)

        expected_arg = {
            "raw_config": {
                "sip_lines": {
                    "1": {
                        'username': username,
                        'auth_username': username,
                        'display_name': display_name,
                        'number': exten,
                        'password': secret,
                        'proxy_ip': proxy_ip,
                        'registrar_ip': registrar_ip
                    }
                }
            }
        }

        device_services.build_line_for_device(device, line)

        config_manager().get.assert_any_call(self.device_id)
        config_manager().get.assert_any_call(configregistrar)
        config_manager().update.assert_called_with(expected_arg)

    @patch('xivo_dao.resources.extension.dao.get')
    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_build_line_for_device_with_a_sip_line_with_proxy_backup(self, config_manager, find_by_line_id, extension_dao_get):
        username = '1234'
        secret = 'password'
        exten = '1250'
        context = 'default'
        display_name = 'Francis Dagobert'
        callerid = '"%s" <%s>' % (display_name, exten)
        proxy_ip = '10.39.5.1'
        registrar_ip = proxy_ip
        proxy_backup = '10.39.5.2'
        configregistrar = 'default'

        line = LineSIP(id=1,
                       device_slot=1,
                       context=context,
                       username=username,
                       name=username,
                       secret=secret,
                       callerid=callerid,
                       configregistrar=configregistrar)
        device = Device(id=self.device_id)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip, proxy_backup)
        config_manager().get.side_effect = (provd_base_config, config_registrar_dict)
        find_by_line_id.return_value = LineExtension(line_id=line.id,
                                                     extension_id=3)
        extension_dao_get.return_value = Extension(exten=exten,
                                                   context=context)

        expected_arg = {
            "raw_config": {
                "sip_lines": {
                    "1": {
                        'username': username,
                        'auth_username': username,
                        'display_name': display_name,
                        'number': exten,
                        'password': secret,
                        'proxy_ip': proxy_ip,
                        'registrar_ip': registrar_ip,
                        'backup_registrar_ip': proxy_backup,
                        'backup_proxy_ip': proxy_backup
                    }
                }
            }
        }

        device_services.build_line_for_device(device, line)

        config_manager().get.assert_any_call(self.device_id)
        config_manager().get.assert_any_call(configregistrar)
        config_manager().update.assert_called_with(expected_arg)

    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_build_line_for_device_with_a_sccp_line(self, config_manager, find_by_line_id):
        exten = '1250'
        context = 'default'
        callerid = 'Francis Dagobert <%s>' % exten
        proxy_ip = '10.39.5.1'
        configregistrar = 'default'

        line = LineSCCP(id=1,
                        device_slot=1,
                        context=context,
                        callerid=callerid,
                        configregistrar=configregistrar)
        device = Device(id=self.device_id)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip)
        config_manager().get.side_effect = (provd_base_config, config_registrar_dict)
        find_by_line_id.return_value = LineExtension(line_id=line.id,
                                                     extension_id=3)

        expected_arg = {
            "raw_config": {
                "sccp_call_managers": {
                    1: {'ip': proxy_ip}
                }
            }
        }

        device_services.build_line_for_device(device, line)

        config_manager().get.assert_any_call(self.device_id)
        config_manager().get.assert_any_call(configregistrar)
        config_manager().update.assert_called_with(expected_arg)

    @patch('xivo_dao.resources.line_extension.dao.find_by_line_id')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_build_line_for_device_with_a_sccp_line_with_proxy_backup(self, config_manager, find_by_line_id):
        exten = '1250'
        context = 'default'
        callerid = 'Francis Dagobert <%s>' % exten
        proxy_ip = '10.39.5.1'
        proxy_backup = '10.39.5.2'
        configregistrar = 'default'

        line = LineSCCP(id=1,
                        device_slot=1,
                        context=context,
                        callerid=callerid,
                        configregistrar=configregistrar)
        device = Device(id=self.device_id)

        provd_base_config = {
            "raw_config": {}
        }

        config_registrar_dict = self._give_me_a_provd_configregistrar(proxy_ip, proxy_backup)
        config_manager().get.side_effect = (provd_base_config, config_registrar_dict)
        find_by_line_id.return_value = LineExtension(line_id=line.id,
                                                     extension_id=3)

        expected_arg = {
            "raw_config": {
                "sccp_call_managers": {
                    1: {'ip': proxy_ip},
                    2: {'ip': proxy_backup}
                }
            }
        }

        device_services.build_line_for_device(device, line)

        config_manager().get.assert_any_call(self.device_id)
        config_manager().get.assert_any_call(configregistrar)
        config_manager().update.assert_called_with(expected_arg)

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_remove_line_from_device(self, config_manager):
        config_dict = {
            "raw_config": {
                "protocol": "sip",
                "sip_lines": {
                    "1": {"username": "1234"},
                    "2": {"username": "5678"}
                }
            }
        }
        config_manager().get.return_value = config_dict
        line = LineSIP(device_slot=2)

        device = Device(id=self.device_id)

        expected_arg = {
            "raw_config": {
                "protocol": "sip",
                "sip_lines": {
                    "1": {"username": "1234"}
                }
            }
        }

        device_services.remove_line_from_device(device, line)

        config_manager().get.assert_called_with(self.device_id)
        config_manager().update.assert_called_with(expected_arg)
        self.assertEquals(0, config_manager().autocreate.call_count)

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_remove_line_from_device_provd_error(self, device_manager, config_manager):
        config_manager().get.side_effect = URLError('urlerror')
        line = LineSIP(device_slot=2)
        device = Device(id=self.device_id)

        self.assertRaises(DataError, device_services.remove_line_from_device, device, line)

        config_manager().get.assert_called_once_with(self.device_id)
        self.assertEquals(config_manager.update.call_count, 0)
        self.assertEquals(config_manager.autocreate.call_count, 0)
        self.assertEquals(device_manager.call_count, 0)

    @patch('xivo_dao.resources.device.services.reset_to_autoprov')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_remove_line_from_device_sip_autoprov(self, config_manager, reset_to_autoprov):
        autoprovid = "autoprov1234"
        config_dict = {
            "raw_config": {
                "protocol": "sip",
                "sip_lines": {
                    "1": {"username": "1234"}
                },
                'funckeys': {
                    '1': {
                        'label': 'bob',
                        'line': 1,
                        'type': 'blf',
                        'value': '1001'
                    }
                }
            }
        }

        config_manager().get.return_value = config_dict
        config_manager().autocreate.return_value = autoprovid
        line = LineSIP(device_slot=1)

        device = Device(id=self.device_id)

        expected_arg_config = {
            "raw_config": {
                "protocol": "sip",
            }
        }

        device_services.remove_line_from_device(device, line)

        config_manager().get.assert_called_with(self.device_id)
        reset_to_autoprov.assert_called_with(device)
        config_manager().update.assert_called_with(expected_arg_config)

    @patch('xivo_dao.resources.device.services.reset_to_autoprov')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_remove_line_from_device_sccp_autoprov(self, config_manager, reset_to_autoprov):
        config_manager().get.return_value = {
            "raw_config": {
                "protocol": "sccp",
            }
        }
        line = LineSCCP(device_slot=1)
        device = Device(id=self.device_id)

        device_services.remove_line_from_device(device, line)

        reset_to_autoprov.assert_called_with(device)

    @patch('xivo_dao.resources.device.services.reset_to_autoprov')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    def test_remove_line_from_device_no_sip_lines(self, config_manager, reset_to_autoprov):
        config_dict = {
            "raw_config": {
                "protocol": "sip",
            }
        }
        config_manager().get.return_value = config_dict
        line = LineSIP(device_slot=2)

        device = Device(id=self.device_id)

        device_services.remove_line_from_device(device, line)

        config_manager().get.assert_called_with(self.device_id)
        self.assertEquals(config_manager().update.call_count, 0)
        self.assertEquals(reset_to_autoprov.update.call_count, 0)

    @patch('xivo_dao.resources.device.services.reset_to_autoprov')
    @patch('xivo_dao.resources.device.provd_converter.reset_config')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_remove_line_from_device_no_funckeys(self, device_manager, config_manager, reset_config, reset_to_autoprov):
        autoprovid = "autoprov1234"
        config_dict = {
            "raw_config": {
                "protocol": "sip",
                "sip_lines": {
                    "1": {"username": "1234"}
                }
            }
        }
        device_dict = {
            "ip": "10.60.0.109",
            "version": "3.2.2.1136",
            "config": self.device_id,
            "id": self.device_id
        }
        line = LineSIP(device_slot=1)

        device = Device(id=self.device_id)

        config_manager().get.return_value = config_dict
        device_manager().get.return_value = device_dict
        config_manager().autocreate.return_value = autoprovid

        try:
            device_services.remove_line_from_device(device, line)
        except:
            self.fail("An exception was raised whereas it should not")

        reset_config.assert_called_once_with(config_dict)
        reset_to_autoprov.assert_called_once_with(device)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_synchronize(self, device_manager):
        device = Device(id=self.device_id)

        device_services.synchronize(device)

        device_manager().synchronize.assert_called_with(self.device_id)

    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_synchronize_with_error(self, device_manager):
        device = Device(id=self.device_id)

        device_manager().synchronize.side_effect = Exception('')

        self.assertRaises(DataError, device_services.synchronize, device)
        device_manager().synchronize.assert_called_with(self.device_id)

    @patch('xivo_dao.resources.line.dao.reset_device', Mock(return_value=None))
    @patch('xivo_dao.resources.device.provd_converter.generate_autoprov_config')
    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_autoprov(self, device_manager, config_manager, generate_autoprov_config):
        device = Device(id=self.device_id)
        autoprov_config_id = 'autoprov123'

        config_device = {}
        config_device['id'] = device.id
        config_device['config'] = 'qwerty'
        config_device['options'] = {'switchboard': True}

        generate_autoprov_config.return_value = autoprov_config_id
        device_manager().get.return_value = config_device
        config_manager().autocreate.return_value = 'autocreate123'

        device_services.reset_to_autoprov(device)

        assert_that(config_device['config'], equal_to(autoprov_config_id))
        assert_that(config_device, is_not(has_item('options')))
        generate_autoprov_config.assert_called_once_with()
        device_manager().get.assert_called_with(self.device_id)
        device_manager().update.assert_called_with(config_device)

    @patch('xivo_dao.helpers.provd_connector.config_manager')
    @patch('xivo_dao.helpers.provd_connector.device_manager')
    def test_autoprov_with_error(self, device_manager, config_manager):
        device = Device(id=self.device_id)

        device_manager().update.side_effect = Exception('')

        self.assertRaises(DataError, device_services.reset_to_autoprov, device)

    def _give_me_a_provd_configregistrar(self, proxy_main, proxy_backup=None):
        config_registrar_dict = {
            'id': 'default',
            'X_type': 'registrar',
            'raw_config': {'X_key': 'xivo'},
            'deletable': False,
            'displayname': 'local',
            'parent_ids': [],
            'proxy_main': proxy_main,
            'registrar_main': proxy_main
        }
        if proxy_backup is not None:
            config_registrar_dict.update({
                'proxy_backup': proxy_backup,
                'registrar_backup': proxy_backup
            })
        return config_registrar_dict
