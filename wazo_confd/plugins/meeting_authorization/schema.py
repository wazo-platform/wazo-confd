# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, OneOf

from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.plugins.meeting.schema import MeetingSchema


class MeetingAuthorizationSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    meeting_uuid = fields.UUID(required=True)
    guest_uuid = fields.UUID(required=True)
    guest_name = fields.String(validate=Length(min=1, max=128), required=True)
    status = fields.String(
        validate=OneOf(['accepted', 'pending', 'rejected']), dump_only=True
    )
    guest_sip_authorization = fields.Method(
        '_guest_sip_authorization',
        required=True,
        allow_none=True,
        dump_only=True,
    )
    creation_time = fields.DateTime(attribute='created_at', dump_only=True)

    def _guest_sip_authorization(self, model):
        if model.status != 'accepted':
            return None

        if not model.guest_endpoint_sip:
            return None

        return MeetingSchema.format_sip_authorization(model.guest_endpoint_sip)


class MeetingAuthorizationIDSchema(BaseSchema):
    authorization_uuid = fields.UUID()
    meeting_uuid = fields.UUID(required=True)
    guest_uuid = fields.UUID()
