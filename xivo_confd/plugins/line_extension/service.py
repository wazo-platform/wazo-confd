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

from xivo_dao.resources.context.model import ContextType
from xivo_dao.resources.context import dao as context_dao
from xivo_dao.resources.incall import dao as incall_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao

from xivo_confd.plugins.line_extension import notifier
from xivo_confd.plugins.line_extension.manager import build_manager

association_manager = build_manager()


def find_by_line_id(line_id):
    return line_extension_dao.find_by_line_id(line_id)


def get_by_line_id(line_id):
    line = line_dao.get(line_id)
    return line_extension_dao.get_by_line_id(line.id)


def find_by_extension_id(extension_id):
    context = context_dao.find_by_extension_id(extension_id)
    if not context:
        return None

    return _find_line_extension_by_type(context, extension_id)


def get_by_extension_id(extension_id):
    context = context_dao.find_by_extension_id(extension_id)
    if not context:
        raise errors.not_found('Extension', id=extension_id)

    line_extension = _find_line_extension_by_type(context, extension_id)
    if not line_extension:
        raise errors.not_found('LineExtension', extension_id=extension_id)

    return line_extension


def _find_line_extension_by_type(context, extension_id):
    if context.type == ContextType.internal:
        return line_extension_dao.find_by_extension_id(extension_id)
    elif context.type == ContextType.incall:
        return incall_dao.find_line_extension_by_extension_id(extension_id)


def get_all_by_line_id(line_id):
    line = line_dao.get(line_id)
    line_extensions = line_extension_dao.find_all_by_line_id(line.id)
    incalls = incall_dao.find_all_line_extensions_by_line_id(line.id)
    return line_extensions + incalls


def associate(line_extension):
    association_manager.associate(line_extension)
    notifier.associated(line_extension)
    return line_extension


def dissociate(line_extension):
    association_manager.dissociate(line_extension)
    notifier.dissociated(line_extension)
    return line_extension
