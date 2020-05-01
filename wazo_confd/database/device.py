# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from sqlalchemy.orm import Load
from sqlalchemy.sql import or_

from xivo_dao.alchemy.userfeatures import UserFeatures
from xivo_dao.alchemy.linefeatures import LineFeatures
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.sccpdevice import SCCPDevice

from xivo_dao.helpers.db_manager import Session


def profile_for_device(device_id):
    query = (
        Session.query(UserFeatures.uuid, LineFeatures.context)
        .join(LineFeatures.user_lines)
        .join(UserLine.main_user_rel)
        .filter(LineFeatures.device_id == device_id)
        .filter(LineFeatures.num == 1)
    )

    return query.first()


def sip_lines_for_device(device_id):
    query = (
        Session.query(LineFeatures, EndpointSIP, Extension)
        .join(LineFeatures.endpoint_sip)
        .join(LineFeatures.user_lines)
        .join(UserLine.main_user_rel)
        .join(LineFeatures.line_extensions)
        .join(LineExtension.main_extension_rel)
        .filter(LineFeatures.device == device_id)
        .options(
            Load(LineFeatures).load_only("id", "configregistrar"),
            Load(EndpointSIP).load_only(
                "uuid", "name"
            ),  # TODO(pc-m): add the load_only
            Load(Extension).load_only("id", "exten"),
        )
    )

    return query.all()


def associate_sccp_device(line, device):
    device_name = "SEP" + device.mac.replace(":", "").upper()

    sccpdevice = (
        Session.query(SCCPDevice).filter(SCCPDevice.device == device_name).first()
    )

    if sccpdevice:
        sccpdevice.line = line.name
    else:
        Session.add(SCCPDevice(name=device_name, device=device_name, line=line.name))
    Session.flush()


def dissociate_sccp_device(line, device):
    device_name = "SEP" + device.mac.replace(":", "").upper()

    (
        Session.query(SCCPDevice)
        .filter(SCCPDevice.device == device_name)
        .filter(SCCPDevice.line == line.name)
        .delete()
    )
    Session.flush()


def template_has_sccp_device(template_id):
    exists_query = (
        Session.query(UserFeatures)
        .join(UserFeatures.main_line_rel)
        .join(UserLine.main_line_rel)
        .filter(
            or_(
                UserFeatures.func_key_template_id == template_id,
                UserFeatures.func_key_private_template_id == template_id,
            )
        )
        .filter(LineFeatures.endpoint_sccp_id != None)  # noqa
        .exists()
    )

    return Session.query(exists_query).scalar()
