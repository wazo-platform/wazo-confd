# -*- coding: utf-8 -*-

# Copyright (C) 2015 Avencall
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

import re

from xivo_confd.helpers.resource import CRUDService
from xivo_confd.resources.devices.model import LineSIPConverter, LineSCCPConverter
from xivo_dao.data_handler.utils.search import SearchResult
from xivo_dao.data_handler import errors


class DeviceService(CRUDService):

    def __init__(self, dao, validator, notifier, search_engine, line_dao):
        super(DeviceService, self).__init__(dao, validator, notifier)
        self.search_engine = search_engine
        self.line_dao = line_dao

    def search(self, parameters):
        return self.search_engine.search(parameters)

    def synchronize(self, device):
        self.dao.synchronize(device)

    def reset_autoprov(self, device):
        self.dao.reset_autoprov(device)
        self.line_dao.reset_device(device.id)


class LineDeviceAssociationService(object):

    def __init__(self, line_dao, line_updater):
        self.line_dao = line_dao
        self.line_updater = line_updater

    def get_line(self, line_id):
        return self.line_dao.get(line_id)

    def associate(self, line, device):
        line.device_id = device.id
        self.line_dao.edit(line)
        self.line_updater.update_lines(device)

    def dissociate(self, line, device):
        line.device_id = None
        self.line_dao.edit(line)
        self.line_updater.update_lines(device)


class LineDeviceUpdater(object):

    def __init__(self, line_dao, extension_dao, line_extension_dao, device_dao):
        self.line_dao = line_dao
        self.extension_dao = extension_dao
        self.line_extension_dao = line_extension_dao
        self.device_dao = device_dao

    def update_lines(self, device):
        converters = self._get_converters(device)
        self.device_dao.update_lines(device, converters)
        if not converters:
            self.device_dao.reset_autoprov(device)

    def _get_converters(self, device):
        converters = []
        lines = self.line_dao.find_all_by_device_id(device.id)
        for line in lines:
            converter = self._line_converter(line)
            if converter:
                converters.append(converter)
        return converters

    def _line_converter(self, line):
        registrar = self.device_dao.get_registrar(line.configregistrar)
        if line.protocol == 'sip':
            return self._sip_line_converter(line, registrar)
        elif line.protocol == 'sccp':
            return LineSCCPConverter(registrar)
        return None

    def _sip_line_converter(self, line, registrar):
        extension = self._find_extension_for_line(line)
        if extension:
            print line
            return LineSIPConverter(registrar,
                                    line,
                                    extension)
        return None

    def _find_extension_for_line(self, line):
        line_extension = self.line_extension_dao.find_by_line_id(line.id)
        if line_extension:
            return self.extension_dao.get(line_extension.extension_id)
        return None


class DeviceValidator(object):

    IP_REGEX = re.compile(r'(1?\d{1,2}|2([0-4][0-9]|5[0-5]))(\.(1?\d{1,2}|2([0-4][0-9]|5[0-5]))){3}$')
    MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2})(:[0-9A-Fa-f]{2}){5}$')

    def __init__(self, device_dao, line_dao):
        self.device_dao = device_dao
        self.line_dao = line_dao

    def validate_create(self, device):
        self._check_invalid_parameters(device)
        self._check_mac_already_exists(device)
        self._check_plugin_exists(device)
        self._check_template_id_exists(device)

    def validate_edit(self, device):
        device_found = self.device_dao.get(device.id)
        self._check_invalid_parameters(device)
        self._check_if_mac_was_modified(device_found, device)
        self._check_plugin_exists(device)
        self._check_template_id_exists(device)

    def validate_delete(self, device):
        self._check_device_is_not_linked_to_line(device)

    def _check_mac_already_exists(self, device):
        if not device.mac:
            return

        existing_device = self.device_dao.find_by('mac', device.mac.lower())
        if existing_device:
            raise errors.resource_exists('Device', mac=device.mac)

    def _check_plugin_exists(self, device):
        if not device.plugin:
            return

        plugins = self.device_dao.plugins()

        if device.plugin not in plugins:
            raise errors.param_not_found('plugin', 'Plugin')

    def _check_template_id_exists(self, device):
        if not device.template_id:
            return

        templates = self.device_dao.device_templates()

        if device.template_id not in templates:
            raise errors.param_not_found('template_id', 'DeviceTemplate')

    def _check_invalid_parameters(self, device):
        if device.ip and not self.IP_REGEX.match(device.ip):
            raise errors.wrong_type('ip', 'IP address', ip=device.ip)
        if device.mac and not self.MAC_REGEX.match(device.mac):
            raise errors.wrong_type('mac', 'MAC address', mac=device.mac)
        if device.options is not None:
            if not isinstance(device.options, dict):
                raise errors.wrong_type('options', 'dict-like structure', options=device.options)
            elif 'switchboard' in device.options and not isinstance(device.options['switchboard'], bool):
                raise errors.wrong_type('options.switchboard', 'boolean', switchboard=device.options['switchboard'])

    def _check_if_mac_was_modified(self, device_found, device):
        if not device.mac or not device_found.mac:
            return

        if device_found.mac.lower() != device.mac.lower():
            self._check_mac_already_exists(device)

    def _check_device_is_not_linked_to_line(self, device):
        linked_lines = self.line_dao.find_all_by_device_id(device.id)
        if linked_lines:
            ids = tuple(l.id for l in linked_lines)
            raise errors.resource_associated('Device', 'Line',
                                             device_id=device.id, line_ids=ids)


class SearchEngine(object):

    PROVD_DEVICE_KEYS = [
        'id',
        'ip',
        'mac',
        'sn',
        'plugin',
        'vendor',
        'model',
        'version',
        'description',
        'options',
    ]

    DEFAULT_ORDER = 'ip'
    DEFAULT_DIRECTION = 'asc'

    def __init__(self, provd_dao):
        self.provd_dao = provd_dao

    def search(self, parameters):
        self.validate_parameters(parameters)
        provd_devices = self.provd_dao.find_all_devices(parameters.get('order', self.DEFAULT_ORDER),
                                                        parameters.get('direction', self.DEFAULT_DIRECTION))

        provd_devices = self.filter_devices(provd_devices,
                                            parameters.get('search'))

        total = len(provd_devices)

        provd_devices = self.paginate_devices(provd_devices,
                                              parameters.get('skip', 0),
                                              parameters.get('limit'))

        items = [self.provd_dao.build_provd_device(device).extract_model()
                 for device in provd_devices]

        return SearchResult(total=total, items=items)

    def validate_parameters(self, parameters):
        if 'order' in parameters:
            if parameters['order'] not in self.PROVD_DEVICE_KEYS:
                raise errors.invalid_ordering(parameters['order'], self.PROVD_DEVICE_KEYS)

    def filter_devices(self, devices, search=None):
        if search is None:
            return devices

        search = search.lower()

        return [device for device in devices
                if self._matches_search(device, search)]

    def _matches_search(self, device, search_lowered):
        for key in self.PROVD_DEVICE_KEYS:
            if key in device and search_lowered in unicode(device[key]).lower():
                return True
        return False

    def paginate_devices(self, devices, skip=0, limit=None):
        if limit:
            return devices[skip:skip + limit]
        return devices[skip:]
