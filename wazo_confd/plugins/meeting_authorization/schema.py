# Copyright 2021-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from base64 import b64encode
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
    guest_sip_authorization = fields.Method(
        '_guest_sip_authorization',
        required=True,
        allow_none=True,
        dump_only=True,
    )

    def _guest_sip_authorization(self, model):
        if model.status != 'accepted':
            return None

        endpoint_sip = model.guest_endpoint_sip
        if not endpoint_sip:
            return None

        username = None
        password = None
        for option, value in endpoint_sip.auth_section_options:
            if option == 'username':
                username = value
            elif option == 'password':
                password = value

        if username is None or password is None:
            return None

        return b64encode('{}:{}'.format(username, password).encode()).decode()


class MeetingAuthorizationIDSchema(BaseSchema):
    authorization_uuid = fields.UUID()
    meeting_uuid = fields.UUID(required=True)
    guest_uuid = fields.UUID()
