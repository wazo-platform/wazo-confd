# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema


class MeetingAuthorizationSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    meeting_uuid = fields.UUID(required=True)
    guest_uuid = fields.UUID(field='guest_uuid', required=True)
    guest_name = fields.String(
        field='guest_name', validate=Length(min=1, max=128), required=True
    )
