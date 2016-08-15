# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.


from xivo_dao.helpers.db_manager import Session

from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension


def find_line_id_for_user(user_id):
    return (Session.query(UserLine.user_id)
            .filter_by(user_id=user_id)
            .scalar())


def check_line_has_users(line_id):
        query = (Session.query(UserLine)
                 .filter(UserLine.line_id == line_id)
                 .filter(UserLine.user_id != None)  # noqa
                 .exists())

        return Session.query(query).scalar()


def has_secondary_users(user_id, line_id):
    exists_query = (Session.query(UserLine)
                    .filter(UserLine.line_id == line_id)
                    .filter(UserLine.user_id != user_id)
                    .filter(UserLine.main_user == False)  # noqa
                    .exists())

    return Session.query(exists_query).scalar()


def find_extension_id_for_line(line_id):
    return (Session.query(LineExtension.extension_id)
            .filter(LineExtension.line_id == line_id)
            .filter(LineExtension.main_extension == True)  # noqa
            .scalar())
