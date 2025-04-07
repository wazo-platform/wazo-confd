# Copyright 2015-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later


from sqlalchemy import Integer, String
from sqlalchemy.orm import aliased
from sqlalchemy.sql import and_, case, cast, func, select
from xivo_dao.alchemy.dialaction import Dialaction
from xivo_dao.alchemy.endpoint_sip import EndpointSIP
from xivo_dao.alchemy.endpoint_sip_section import EndpointSIPSection
from xivo_dao.alchemy.endpoint_sip_section_option import EndpointSIPSectionOption
from xivo_dao.alchemy.extension import Extension
from xivo_dao.alchemy.incall import Incall
from xivo_dao.alchemy.line_extension import LineExtension
from xivo_dao.alchemy.linefeatures import LineFeatures as Line
from xivo_dao.alchemy.rightcall import RightCall
from xivo_dao.alchemy.rightcallmember import RightCallMember
from xivo_dao.alchemy.user_line import UserLine
from xivo_dao.alchemy.userfeatures import UserFeatures as User
from xivo_dao.alchemy.voicemail import Voicemail
from xivo_dao.helpers.db_manager import Session

COLUMNS = (
    'uuid',
    'subscription_type',
    'firstname',
    'lastname',
    'email',
    'mobile_phone_number',
    'outgoing_caller_id',
    'language',
    'call_permission_password',
    'enabled',
    'ring_seconds',
    'simultaneous_calls',
    'supervision_enabled',
    'call_transfer_enabled',
    'dtmf_hangup_enabled',
    'call_record_outgoing_external_enabled',
    'call_record_outgoing_internal_enabled',
    'call_record_incoming_external_enabled',
    'call_record_incoming_internal_enabled',
    'online_call_record_enabled',
    'userfield',
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
    'incall_context',
    'call_permissions',
)


def export_query(tenant_uuid, separator=";"):
    ordered_incalls = aliased(
        Session.query(
            Extension.exten.label('exten'),
            Extension.context.label('context'),
            User.id.label('user_id'),
        )
        .select_from(Incall)
        .join(
            Dialaction,
            and_(
                Dialaction.category == 'incall',
                Dialaction.action == 'user',
                cast(Dialaction.categoryval, Integer) == Incall.id,
            ),
        )
        .join(User, cast(Dialaction.actionarg1, Integer) == User.id)
        .join(
            Extension,
            and_(
                Extension.type == 'incall',
                cast(Extension.typeval, Integer) == Incall.id,
            ),
        )
        .order_by(Extension.exten, Extension.context)
        .subquery()
    )

    grouped_incalls = aliased(
        Session.query(
            ordered_incalls.c.user_id,
            func.string_agg(ordered_incalls.c.exten, separator).label('exten'),
            func.string_agg(ordered_incalls.c.context, separator).label('context'),
        )
        .group_by(ordered_incalls.c.user_id)
        .subquery()
    )

    ordered_call_permissions = aliased(
        Session.query(
            RightCall.name, cast(RightCallMember.typeval, Integer).label('user_id')
        )
        .join(RightCallMember, RightCallMember.rightcallid == RightCall.id)
        .join(
            User,
            and_(
                RightCallMember.type == 'user',
                cast(RightCallMember.typeval, Integer) == User.id,
            ),
        )
        .order_by(RightCall.name)
        .subquery()
    )

    grouped_call_permissions = aliased(
        Session.query(
            ordered_call_permissions.c.user_id,
            func.string_agg(ordered_call_permissions.c.name, separator).label('name'),
        )
        .group_by(ordered_call_permissions.c.user_id)
        .subquery()
    )

    columns = (
        User.uuid,
        User.subscription_type,
        User.firstname,
        User.lastname,
        User.email,
        User.mobile_phone_number,
        User.outgoing_caller_id,
        User.language,
        User.call_permission_password,
        case([(User.enabled, '1')], else_='0'),
        cast(User.ring_seconds, String),
        cast(User.simultaneous_calls, String),
        cast(User.enablehint, String),
        cast(User.enablexfer, String),
        cast(User.dtmf_hangup, String),
        case([(User.call_record_outgoing_external_enabled, '1')], else_='0'),
        case([(User.call_record_outgoing_internal_enabled, '1')], else_='0'),
        case([(User.call_record_incoming_external_enabled, '1')], else_='0'),
        case([(User.call_record_incoming_internal_enabled, '1')], else_='0'),
        cast(User.enableonlinerec, String),
        User.userfield,
        Voicemail.name,
        Voicemail.number,
        Voicemail.context,
        Voicemail.password,
        Voicemail.email,
        cast(Voicemail.attach, String),
        cast(Voicemail.deletevoicemail, String),
        cast(cast(Voicemail.ask_password, Integer), String),
        case(
            [
                (Line.endpoint_sip_uuid != None, 'sip'),  # noqa
                (Line.endpoint_sccp_id != None, 'sccp'),  # noqa
                (Line.endpoint_custom_id != None, 'custom'),  # noqa
            ],
            else_='',
        ),
        Line.provisioning_code,
        func.coalesce(Extension.context, Line.context),
        select([EndpointSIPSectionOption.value])
        .where(
            and_(
                EndpointSIP.uuid == EndpointSIPSection.endpoint_sip_uuid,
                EndpointSIPSection.type == 'auth',
                EndpointSIPSectionOption.endpoint_sip_section_uuid
                == EndpointSIPSection.uuid,
                EndpointSIPSectionOption.key == 'username',
            )
        )
        .as_scalar(),
        select([EndpointSIPSectionOption.value])
        .where(
            and_(
                EndpointSIP.uuid == EndpointSIPSection.endpoint_sip_uuid,
                EndpointSIPSection.type == 'auth',
                EndpointSIPSectionOption.endpoint_sip_section_uuid
                == EndpointSIPSection.uuid,
                EndpointSIPSectionOption.key == 'password',
            )
        )
        .as_scalar(),
        Extension.exten,
        grouped_incalls.c.exten,
        grouped_incalls.c.context,
        grouped_call_permissions.c.name,
    )

    query = (
        Session.query(*columns)
        .outerjoin(User.voicemail)
        .outerjoin(User.main_line_rel)
        .outerjoin(UserLine.main_line_rel)
        .outerjoin(Line.endpoint_sip)
        .outerjoin(Line.line_extensions)
        .outerjoin(LineExtension.main_extension_rel)
        .outerjoin(grouped_incalls, User.id == grouped_incalls.c.user_id)
        .outerjoin(
            grouped_call_permissions, User.id == grouped_call_permissions.c.user_id
        )
        .filter(User.tenant_uuid == tenant_uuid)
    )

    return COLUMNS, query
