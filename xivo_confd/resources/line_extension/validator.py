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

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao


def validate_model(line_extension):
    missing = line_extension.missing_parameters()
    if missing:
        raise errors.missing(*missing)


def validate_line(line_extension):
    try:
        line_dao.get(line_extension.line_id)
    except NotFoundError:
        raise errors.param_not_found('line_id', 'Line')


def validate_extension(line_extension):
    try:
        extension_dao.get(line_extension.extension_id)
    except NotFoundError:
        raise errors.param_not_found('extension_id', 'Extension')


def validate_line_not_associated_to_extension(line_extension):
    line_extension = line_extension_dao.find_by_line_id(line_extension.line_id)
    if line_extension:
        raise errors.resource_associated('Line',
                                         'Extension',
                                         line_id=line_extension.line_id,
                                         extension_id=line_extension.extension_id)


def validate_associated_to_user(line_extension):
    user_lines = user_line_dao.find_all_by_line_id(line_extension.line_id)
    if not user_lines:
        raise errors.missing_association('Line', 'User', line_id=line_extension.line_id)


def validate_associated(line_extension):
    line_extensions = _all_line_extensions(line_extension.line_id)
    if line_extension not in line_extensions:
        raise errors.missing_association('Line',
                                         'Extension',
                                         line_id=line_extension.line_id,
                                         extension_id=line_extension.extension_id)


def _all_line_extensions(line_id):
    return (line_extension_dao.find_all_by_line_id(line_id) +
            incall_dao.find_all_line_extensions_by_line_id(line_id))
