# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, OneOf

from wazo_confd.helpers.mallow import BaseSchema


class MeetingAuthorizationSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    meeting_uuid = fields.UUID(required=True)
    guest_uuid = fields.UUID(required=True)
    guest_name = fields.String(validate=Length(min=1, max=128), required=True)
    status = fields.String(
        validate=OneOf(['accepted', 'pending', 'rejected']), dump_only=True
    )


class MeetingAuthorizationIDSchema(BaseSchema):
    authorization_uuid = fields.UUID()
    meeting_uuid = fields.UUID(required=True)
    guest_uuid = fields.UUID()
