# -*- coding: utf-8 -*-

# Copyright (C) 2013-2015 Avencall
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

from . import dao
from . import validator
from .model import DeviceOrdering
from . import notifier

from urllib2 import URLError

from xivo_dao.resources import errors
from xivo_dao.helpers import provd_connector
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.exception import DataError
from xivo_dao.resources.device import provd_converter


def get(device_id):
    return dao.get(device_id)


def search(parameters):
    if 'order' in parameters:
        DeviceOrdering.validate_order(parameters['order'])
    if 'direction' in parameters:
        DeviceOrdering.validate_direction(parameters['direction'])
    if 'skip' in parameters:
        _validate_skip(parameters['skip'])
    if 'limit' in parameters:
        _validate_limit(parameters['limit'])

    return dao.search(**parameters)


def _validate_skip(skip):
    if not isinstance(skip, int) or skip < 0:
        raise errors.wrong_type('skip', 'positive number', skip=skip)
    return int(skip)


def _validate_limit(limit):
    if not (isinstance(limit, int) and limit > 0):
        raise errors.wrong_type('limit', 'positive number', limit=limit)
    return int(limit)


def create(device):
    validator.validate_create(device)
    device = dao.create(device)
    notifier.created(device)
    return device


def edit(device):
    validator.validate_edit(device)
    dao.edit(device)
    notifier.edited(device)
    return device


def delete(device):
    validator.validate_delete(device)
    dao.delete(device)
    line_dao.reset_device(device.id)
    notifier.deleted(device)


def associate_line_to_device(device, line):
    line.device_id = str(device.id)
    line_dao.edit(line)
    provd_converter.link_device_config(device)
    rebuild_device_config(device)


def rebuild_device_config(device):
    lines_device = line_dao.find_all_by_device_id(device.id)
    try:
        for line in lines_device:
            build_line_for_device(device, line)
    except Exception as e:
        raise DataError.on_action('associate', 'LineDevice', e)


def build_line_for_device(device, line):
    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(device.id)
    confregistrar = provd_config_manager.get(line.configregistrar)
    line_extension = line_extension_dao.find_by_line_id(line.id)
    if line_extension:
        if line.protocol == 'sip':
            extension = extension_dao.get(line_extension.extension_id)
            provd_converter.populate_sip_line(config, confregistrar, line, extension)
        elif line.protocol == 'sccp':
            provd_converter.populate_sccp_line(config, confregistrar)


def remove_line_from_device(device, line):
    try:
        if line.protocol == 'sccp':
            _remove_line_from_device_sccp(device)
        elif line.protocol == 'sip':
            _remove_line_from_device_sip(device, line)
    except URLError as e:
        raise DataError.on_action('dissociate', 'LineDevice', e)


def _remove_line_from_device_sccp(device):
    reset_to_autoprov(device)


def _remove_line_from_device_sip(device, line):
    provd_config_manager = provd_connector.config_manager()
    config = provd_config_manager.get(device.id)
    if 'sip_lines' in config['raw_config']:
        del config['raw_config']['sip_lines'][str(line.device_slot)]
        if len(config['raw_config']['sip_lines']) == 0:
            provd_converter.reset_config(config)
            reset_to_autoprov(device)
        provd_config_manager.update(config)


def remove_all_line_from_device(device):
    provd_config_manager = provd_connector.config_manager()
    try:
        config = provd_config_manager.get(device.id)
        provd_converter.reset_config(config)
        provd_config_manager.update(config)
    except URLError as e:
        raise DataError.on_action('dissociate', 'LineDevice', e)


def reset_to_autoprov(device):
    provd_device_manager = provd_connector.device_manager()
    try:
        provd_device = provd_device_manager.get(device.id)
        provd_device['config'] = provd_converter.generate_autoprov_config()
        provd_device.pop('options', None)
        provd_device_manager.update(provd_device)
    except Exception as e:
        raise DataError.on_action('reset to autoprov', 'Device', e)
    else:
        remove_all_line_from_device(device)
        line_dao.reset_device(device.id)


def synchronize(device):
    try:
        provd_device_manager = provd_connector.device_manager()
        provd_device_manager.synchronize(device.id)
    except Exception as e:
        raise DataError.on_action('synchronize', 'Device', e)
