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
from xivo_dao.data_handler.user import dao as user_dao


def delete_all():
    remote_exec(_delete_all)


def _delete_all(channel):
    from xivo_dao.data_handler.user import services as user_services
    from xivo_dao.data_handler.user_line_extension import services as ule_services

    for user in user_services.find_all():

        ules = ule_services.find_all_by_user_id(user.id)
        for ule in ules:
            ule_services.delete(ule)

        user_services.delete(user)


def create_user(userinfo):
    remote_exec(_create_user, userinfo=userinfo)


def _create_user(channel, userinfo):
    from xivo_dao.data_handler.user import services as user_services
    from xivo_dao.data_handler.user.model import User

    user = User(**userinfo)
    user_services.create(user)


def find_user_by_name(name):
    firstname, lastname = name.split(" ")
    return user_dao.find_user(firstname, lastname)
