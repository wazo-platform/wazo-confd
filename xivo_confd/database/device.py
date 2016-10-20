# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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
from sqlalchemy.sql import or_

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.usersip import UserSIP
from xivo_dao.alchemy.sccpdevice import SCCPDevice

from xivo_dao.helpers.db_manager import Session


def profile_for_device(device_id):
    query = (Session.query(UserFeatures.uuid,
                           LineFeatures.context)
             .join(LineFeatures.user_lines)
             .join(UserLine.main_user_rel)
             .filter(LineFeatures.device_id == device_id)
             .filter(LineFeatures.num == 1)
             )

    return query.first()


def sip_lines_for_device(device_id):
    query = (Session.query(LineFeatures, UserSIP, Extension)
             .join(LineFeatures.endpoint_sip)
             .join(LineFeatures.user_lines)
             .join(UserLine.main_user_rel)
             .join(LineFeatures.line_extensions)
             .join(LineExtension.main_extension_rel)
             .filter(LineFeatures.device == device_id)
             .options(
                 Load(LineFeatures).load_only("id", "configregistrar"),
                 Load(UserSIP).load_only("id", "callerid", "name", "secret"),
                 Load(Extension).load_only("id", "exten"))
             )

    return query.all()


def associate_sccp_device(line, device):
    device_name = "SEP" + device.mac.replace(":", "").upper()

    sccpdevice = (Session.query(SCCPDevice)
                  .filter(SCCPDevice.device == device_name)
                  .first())

    if sccpdevice:
        sccpdevice.line = line.number
    else:
        Session.add(SCCPDevice(name=device_name,
                               device=device_name,
                               line=line.number))
    Session.flush()


def dissociate_sccp_device(line, device):
    device_name = "SEP" + device.mac.replace(":", "").upper()

    (Session.query(SCCPDevice)
     .filter(SCCPDevice.device == device_name)
     .filter(SCCPDevice.line == line.number)
     .delete())
    Session.flush()


def template_has_sccp_device(template_id):
    exists_query = (Session.query(UserFeatures)
                    .join(UserFeatures.main_line_rel)
                    .join(UserLine.main_line_rel)
                    .filter(or_(UserFeatures.func_key_template_id == template_id,
                                UserFeatures.func_key_private_template_id == template_id))
                    .filter(LineFeatures.endpoint == "sccp")
                    .exists())

    return Session.query(exists_query).scalar()
