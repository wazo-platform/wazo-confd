# -*- coding: utf-8 -*-

# Copyright (C) 2014 Avencall
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

from xivo_dao.resources.extension import dao as extension_dao
from xivo_dao.resources.line import dao as line_dao
from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.user_line import dao as user_line_dao
from xivo_dao.resources.line_extension import dao as line_extension_dao
from xivo import caller_id


def associate_user_line(user_line):
    created_user_line = user_line_dao.associate(user_line)
    main_user_line = user_line_dao.find_main_user_line(created_user_line.line_id)
    fix_associations(main_user_line)
    return created_user_line


def associate_line_extension(line_extension):
    created_line_extension = line_extension_dao.associate(line_extension)
    main_user_line = user_line_dao.find_main_user_line(created_line_extension.line_id)
    if main_user_line:
        fix_associations(main_user_line)
    return created_line_extension


def fix_associations(main_user_line):
    main_user, line, extension = find_resources(main_user_line)
    update_resources(main_user, line, extension)


def find_resources(main_user_line):
    main_user = user_dao.get(main_user_line.user_id)
    line = line_dao.get(main_user_line.line_id)
    extension = find_extension(main_user_line.line_id)
    return main_user, line, extension


def find_extension(line_id):
    line_extension = line_extension_dao.find_by_line_id(line_id)
    if line_extension:
        return extension_dao.get(line_extension.extension_id)
    return None


def update_resources(main_user, line, extension=None):
    update_caller_id(main_user, line, extension)
    update_line(main_user, line)
    if extension:
        update_exten_and_context(main_user, line, extension)


def update_caller_id(main_user, line, extension=None):
    exten = extension.exten if extension else None
    line.callerid = caller_id.assemble_caller_id(main_user.fullname, exten)
    line_dao.edit(line)


def update_line(main_user, line):
    line_dao.update_xivo_userid(line, main_user)


def update_exten_and_context(main_user, line, extension):
    extension_dao.associate_destination(extension.id, 'user', main_user.id)
    line_dao.associate_extension(extension, line.id)


def dissociate_line_extension(line_extension):
    line_extension_dao.dissociate(line_extension)
    extension = extension_dao.get(line_extension.extension_id)
    remove_exten_and_context(extension)


def remove_exten_and_context(extension):
    line_dao.dissociate_extension(extension)
    extension_dao.dissociate_extension(extension.id)


def dissociate_user_line(user_line):
    user_line_dao.dissociate(user_line)
    if user_line.main_user:
        fix_main_user_dissociation(user_line.line_id)


def fix_main_user_dissociation(line_id):
    remove_caller_id(line_id)
    extension = find_extension(line_id)
    if extension:
        remove_exten_and_context(extension)


def remove_caller_id(line_id):
    line_dao.delete_user_references(line_id)
