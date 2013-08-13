# -*- coding: utf-8 -*-

# Copyright (C) 2013 Avencall
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

from remote import remote_exec


def delete_all():
    remote_exec(_delete_all)


def _delete_all(channel):
    from xivo_dao.data_handler.extension import services as extension_services
    from xivo_dao.data_handler.user_line_extension import services as ule_services

    hidden_extensions = extension_services.find_all(commented=True)
    visible_extensions = extension_services.find_all()

    extensions = [e for e in hidden_extensions + visible_extensions if e.context != 'xivo-features']

    for extension in extensions:

        ules = ule_services.find_all_by_extension_id(extension.id)
        for ule in ules:
            ule_services.delete(ule)

        extension_services.delete(extension)


def create_extensions(extensions):
    extensions = [dict(e) for e in extensions]
    remote_exec(_create_extensions, extensions=extensions)


def _create_extensions(channel, extensions):
    from xivo_dao.data_handler.extension import services as extension_services
    from xivo_dao.data_handler.extension.model import Extension

    for extinfo in extensions:
        extension = Extension(**extinfo)
        extension_services.create(extension)
