# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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
from xivo_dao.alchemy.func_key import FuncKey
from xivo_dao.alchemy.func_key_dest_user import FuncKeyDestUser
from xivo_dao.alchemy.func_key_mapping import FuncKeyMapping
from xivo_dao.alchemy.func_key_template import FuncKeyTemplate


def find_all_dst_user(user_id):

    query = (Session.query(FuncKeyTemplate)
             .join(FuncKeyMapping, FuncKeyTemplate.id == FuncKeyMapping.template_id)
             .join(FuncKey, FuncKeyMapping.func_key_id == FuncKey.id)
             .join(FuncKeyDestUser, FuncKey.id == FuncKeyDestUser.func_key_id)
             .filter(FuncKeyDestUser.user_id == user_id)
             )

    return query.all()
