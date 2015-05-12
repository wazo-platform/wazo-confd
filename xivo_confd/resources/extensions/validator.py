# -*- coding: utf-8 -*-

# Copyright (C) 2014-2015 Avencall
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
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao


def validate_create(extension):
    validate_missing_parameters(extension)
    validate_invalid_parameters(extension)
    validate_context_exists(extension)
    validate_extension_available(extension)
    validate_extension_in_range(extension)


def validate_edit(extension):
    validate_missing_parameters(extension)
    validate_invalid_parameters(extension)
    validate_context_exists(extension)
    validate_extension_available_for_edit(extension)
    validate_extension_in_range(extension)


def validate_delete(extension):
    validate_extension_exists(extension)
    validate_extension_not_associated(extension.id)


def validate_invalid_parameters(extension):
    if not extension.exten:
        raise errors.missing('exten')
    if not extension.context:
        raise errors.missing('context')
    if extension.commented not in [True, False]:
        raise errors.wrong_type('commented', 'boolean')


def validate_missing_parameters(extension):
    missing = extension.missing_parameters()
    if missing:
        raise errors.missing(*missing)


def validate_context_exists(extension):
    existing_context = context_dao.get(extension.context)
    if not existing_context:
        raise errors.param_not_found('context', 'Context')


def validate_extension_available(extension):
    existing_extension = extension_dao.find_by_exten_context(extension.exten, extension.context)
    if existing_extension:
        raise errors.resource_exists('Extension',
                                     exten=extension.exten, context=extension.context)


def validate_extension_in_range(extension):
    if not is_extension_valid_for_context(extension):
        raise errors.outside_context_range(extension.exten, extension.context)


def validate_extension_exists(extension):
    extension_dao.get(extension.id)


def validate_extension_not_associated(extension_id):
    extension_type, typeval = extension_dao.get_type_typeval(extension_id)

    # extensions that are created or dissociated are set to these values by default
    if extension_type != 'user' and typeval != '0':
        raise errors.resource_associated('Extension', extension_type,
                                         extension_id=extension_id, associated_id=typeval)

    line_extension = line_extension_dao.find_by_extension_id(extension_id)
    if line_extension:
        raise errors.resource_associated('Extension', 'Line',
                                         extension_id=extension_id, line_id=line_extension.line_id)


def validate_extension_available_for_edit(extension):
    existing_extension = extension_dao.get(extension.id)

    if existing_extension.exten != extension.exten or \
       existing_extension.context != extension.context:
        validate_extension_available(extension)


def is_extension_valid_for_context(extension):
    exten = _validate_exten(extension)
    context_ranges = context_dao.find_all_context_ranges(extension.context)
    return is_extension_included_in_ranges(exten, context_ranges)


def _validate_exten(extension):
    if not extension.exten.isdigit():
        raise errors.wrong_type('exten', 'numeric string')
    return extension.exten


def is_extension_included_in_ranges(exten, context_ranges):
    for context_range in context_ranges:
        if context_range.in_range(exten):
            return True
    return False


def is_extension_valid_for_context_range(extension, context_range):
    exten = _validate_exten(extension)
    context_ranges = context_dao.find_all_specific_context_ranges(extension.context, context_range)
    return is_extension_included_in_ranges(exten, context_ranges)
