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

import random

from . import notifier
from . import dao

from xivo_dao.helpers import errors
from xivo_dao.resources.device import services as device_services
from xivo_dao.resources.device import dao as device_dao
from xivo_dao.resources.context import services as context_services
from xivo import caller_id


def get(line_id):
    return dao.get(line_id)


def get_by_user_id(user_id):
    return dao.get_by_user_id(user_id)


def get_by_number_context(number, context):
    return dao.get_by_number_context(number, context)


def find_all(order=None):
    return dao.find_all(order=order)


def find_all_by_name(name):
    return dao.find_all_by_name(name)


def find_all_by_protocol(protocol):
    return dao.find_all_by_protocol(protocol)


def find_all_by_device_id(name):
    return dao.find_all_by_device_id(name)


def create(line):
    _validate(line)
    line.provisioning_extension = make_provisioning_id()
    line = dao.create(line)
    notifier.created(line)
    return line


def edit(line):
    _validate(line)
    dao.edit(line)
    _update_device(line)
    notifier.edited(line)


def delete(line):
    dao.delete(line)
    _delete_line_from_device(line)
    notifier.deleted(line)


def _update_device(line):
    if hasattr(line, 'device_id') and line.device_id:
        device = device_dao.find(line.device_id)
        if device:
            device_services.rebuild_device_config(device)


def _delete_line_from_device(line):
    if hasattr(line, 'device_id') and line.device_id:
        device = device_dao.find(line.device_id)
        if device:
            device_services.remove_line_from_device(device, line)


def update_callerid(user):
    line = dao.find_by_user_id(user.id)
    if line:
        callerid, cid_name, cid_number = caller_id.build_caller_id('', user.fullname, line.number)
        line.callerid = callerid
        edit(line)


def _validate(line):
    _check_missing_parameters(line)
    _check_invalid_parameters(line)
    _check_invalid_context(line)


def _check_missing_parameters(line):
    missing = line.missing_parameters()
    if missing:
        raise errors.missing(*missing)


def _check_invalid_parameters(line):
    if line.context.strip() == '':
        raise errors.missing('context')
    try:
        line.device_slot = int(line.device_slot)
    except ValueError:
        raise errors.wrong_type('device_slot', 'positive numeric', device_slot=line.device_slot)
    if line.device_slot <= 0:
        raise errors.wrong_type('device_slot', 'positive numeric', device_slot=line.device_slot)


def _check_invalid_context(line):
    context = context_services.find_by_name(line.context)
    if not context:
        raise errors.param_not_found('context', 'Context')


def make_provisioning_id():
    provd_id = _generate_random_digits()
    while dao.provisioning_id_exists(provd_id):
        provd_id = _generate_random_digits()
    return provd_id


def _generate_random_digits():
    digitrange = range(1, 9)
    digits = [str(random.choice(digitrange)) for r in range(6)]
    provd_id = ''.join(digits)
    return provd_id
