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

from sqlalchemy.orm import Load

from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.user_line import UserLine as UserLine
from xivo_dao.alchemy.usersip import UserSIP

from xivo_dao.helpers.db_manager import Session


def sip_lines_for_device(device_id):
    query = (Session.query(LineFeatures, UserSIP, Extension)
             .join(LineFeatures.sip_endpoint)
             .join(LineFeatures.user_lines)
             .join(UserLine.main_user_rel)
             .join(UserLine.main_extension_rel)
             .filter(LineFeatures.device == device_id)
             .options(
                 Load(LineFeatures).load_only("id", "configregistrar"),
                 Load(UserSIP).load_only("id", "callerid", "name", "secret"),
                 Load(Extension).load_only("id", "exten"))
             )

    return query.all()
