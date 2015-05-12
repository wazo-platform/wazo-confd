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

import re

from . import dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.helpers import errors

IP_REGEX = re.compile(r'(1?\d{1,2}|2([0-4][0-9]|5[0-5]))(\.(1?\d{1,2}|2([0-4][0-9]|5[0-5]))){3}$')
MAC_REGEX = re.compile(r'^([0-9A-Fa-f]{2})(:[0-9A-Fa-f]{2}){5}$')


def validate_create(device):
    _check_invalid_parameters(device)
    _check_mac_already_exists(device)
    _check_plugin_exists(device)
    _check_template_id_exists(device)


def validate_edit(device):
    device_found = dao.find(device.id)
    _check_invalid_parameters(device)
    _check_if_mac_was_modified(device_found, device)
    _check_plugin_exists(device)
    _check_template_id_exists(device)


def validate_delete(device):
    _check_device_is_not_linked_to_line(device)


def _check_mac_already_exists(device):
    if not device.mac:
        return

    existing_device = dao.mac_exists(device.mac)
    if existing_device:
        raise errors.resource_exists('Device', mac=device.mac)


def _check_plugin_exists(device):
    if not device.plugin:
        return

    if not dao.plugin_exists(device.plugin):
        raise errors.param_not_found('plugin', 'Plugin')


def _check_template_id_exists(device):
    if not device.template_id:
        return

    if not dao.template_id_exists(device.template_id):
        raise errors.param_not_found('template_id', 'DeviceTemplate')


def _check_invalid_parameters(device):
    if device.ip and not IP_REGEX.match(device.ip):
        raise errors.wrong_type('ip', 'IP address', ip=device.ip)
    if device.mac and not MAC_REGEX.match(device.mac):
        raise errors.wrong_type('mac', 'MAC address', mac=device.mac)
    if device.options is not None:
        if not isinstance(device.options, dict):
            raise errors.wrong_type('options', 'dict-like structure', options=device.options)
        elif 'switchboard' in device.options and not isinstance(device.options['switchboard'], bool):
            raise errors.wrong_type('options.switchboard', 'boolean', switchboard=device.options['switchboard'])


def _check_if_mac_was_modified(device_found, device):
    if not device.mac or not device_found.mac:
        return

    if device_found.mac != device.mac:
        _check_mac_already_exists(device)


def _check_device_is_not_linked_to_line(device):
    linked_lines = line_dao.find_all_by_device_id(device.id)
    if linked_lines:
        ids = tuple(l.id for l in linked_lines)
        raise errors.resource_associated('Device', 'Line',
                                         device_id=device.id, line_ids=ids)
