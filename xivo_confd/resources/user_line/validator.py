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

from xivo_dao.resources import errors
from xivo_dao.resources.exception import NotFoundError
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_device import validator as line_device_validator


def validate_association(user_line):
    _validate_missing_parameters(user_line)
    _validate_invalid_parameters(user_line)
    _validate_user_id(user_line)
    _validate_line_id(user_line)
    _validate_user_not_associated_with_line(user_line)


def validate_dissociation(user_line):
    _validate_user_id(user_line)
    _validate_line_id(user_line)
    _validate_user_has_line(user_line)
    _is_allowed_to_dissociate(user_line)
    line_device_validator.validate_no_device(user_line.line_id)


def _validate_missing_parameters(user_line):
    missing = user_line.missing_parameters()
    if len(missing) > 0:
        raise errors.missing(*missing)


def _validate_invalid_parameters(user_line):
    if not isinstance(user_line.user_id, int):
        raise errors.wrong_type('user_id', 'positive integer')
    if not isinstance(user_line.line_id, int):
        raise errors.wrong_type('line_id', 'positive integer')
    if hasattr(user_line, 'main_user') and not isinstance(user_line.main_user, bool):
        raise errors.wrong_type('main_user', 'boolean')
    if hasattr(user_line, 'main_line') and not isinstance(user_line.main_line, bool):
        raise errors.wrong_type('main_line', 'boolean')


def _validate_user_id(user_line):
    try:
        return user_dao.get(user_line.user_id)
    except NotFoundError:
        raise errors.param_not_found('user_id', 'User')


def _validate_line_id(user_line):
    try:
        return line_dao.get(user_line.line_id)
    except NotFoundError:
        raise errors.param_not_found('line_id', 'Line')


def _validate_user_has_line(user_line):
    user_lines = user_line_dao.find_all_by_user_id(user_line.user_id)
    if len(user_lines) == 0:
        raise errors.missing_association('User',
                                         'Line',
                                         user_id=user_line.user_id,
                                         line_id=user_line.line_id)


def _validate_user_not_associated_with_line(user_line):
    existing = user_line_dao.find_all_by_user_id(user_line.user_id)
    if len(existing) > 0:
        raise errors.resource_associated('User',
                                         'Line',
                                         user_id=user_line.user_id,
                                         line_id=user_line.line_id)


def _is_allowed_to_dissociate(user_line):
    if user_line.main_user is True and user_line_dao.line_has_secondary_user(user_line):
        raise errors.secondary_users(line_id=user_line.line_id)
