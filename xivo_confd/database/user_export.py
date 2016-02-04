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


from sqlalchemy.sql import cast, func, and_
from sqlalchemy import String, Integer
from sqlalchemy.orm import aliased

from xivo_dao.helpers.db_manager import Session
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.alchemy.cti_profile import CtiProfile
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.usersip import UserSIP as SIP
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.dialaction import Dialaction


COLUMNS = ('uuid',
           'entity_id',
           'firstname',
           'lastname',
           'email',
           'mobile_phone_number',
           'outgoing_caller_id',
           'language',
           'ring_seconds',
           'simultaneous_calls',
           'supervision_enabled',
           'call_transfer_enabled',
           'userfield',
           'username',
           'password',
           'cti_profile_name',
           'cti_profile_enabled',
           'voicemail_name',
           'voicemail_number',
           'voicemail_context',
           'voicemail_password',
           'voicemail_email',
           'voicemail_attach_audio',
           'voicemail_delete_messages',
           'voicemail_ask_password',
           'line_protocol',
           'provisioning_code',
           'context',
           'sip_username',
           'sip_secret',
           'exten',
           'incall_exten',
           'incall_context')


def export_query(separator=";"):
    ordered_incalls = aliased(
        Session.query(
            Incall.exten.label('exten'),
            Incall.context.label('context'),
            User.id.label('user_id')
        )
        .join(Dialaction,
              and_(Dialaction.category == 'incall',
                   Dialaction.action == 'user',
                   cast(Dialaction.categoryval, Integer) == Incall.id))
        .join(User,
              cast(Dialaction.actionarg1, Integer) == User.id)
        .order_by(Incall.exten, Incall.context)
        .subquery()
    )

    grouped_incalls = aliased(
        Session.query(
            ordered_incalls.c.user_id,
            func.string_agg(ordered_incalls.c.exten, separator).label('exten'),
            func.string_agg(ordered_incalls.c.context, separator).label('context')
        )
        .group_by(ordered_incalls.c.user_id)
        .subquery()
    )

    columns = (
        User.uuid,
        cast(User.entity_id, String),
        User.firstname,
        User.lastname,
        User.email,
        User.mobile_phone_number,
        User.outgoing_caller_id,
        User.language,
        cast(User.ring_seconds, String),
        cast(User.simultaneous_calls, String),
        cast(User.enablehint, String),
        cast(User.enablexfer, String),
        User.userfield,
        User.username,
        User.password,
        CtiProfile.name,
        cast(User.enableclient, String),
        Voicemail.name,
        Voicemail.number,
        Voicemail.context,
        Voicemail.password,
        Voicemail.email,
        cast(Voicemail.attach, String),
        cast(Voicemail.deletevoicemail, String),
        cast(cast(Voicemail.ask_password, Integer), String),
        Line.endpoint,
        Line.provisioning_code,
        func.coalesce(Extension.context, Line.context),
        SIP.name,
        SIP.secret,
        Extension.exten,
        grouped_incalls.c.exten,
        grouped_incalls.c.context
    )

    query = (
        Session.query(*columns)
        .outerjoin(User.voicemail)
        .outerjoin(User.cti_profile)
        .outerjoin(User.main_line_rel)
        .outerjoin(UserLine.main_line_rel)
        .outerjoin(Line.sip_endpoint)
        .outerjoin(UserLine.extensions)
        .outerjoin(grouped_incalls,
                   User.id == grouped_incalls.c.user_id)
    )

    return COLUMNS, query
