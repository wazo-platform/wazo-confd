# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from base64 import b64encode
from marshmallow import fields
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


class MeetingSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    owner_uuids = fields.List(fields.UUID())
    name = fields.String(validate=Length(max=512), required=True)
    ingress_http_uri = fields.Method('_uri', dump_only=True)
    guest_sip_authorization = fields.Method('_guest_sip_authorization', dump_only=True)
    links = ListLink(Link('meetings', field='uuid'))
    tenant_uuid = fields.String(dump_only=True)

    def _uri(self, meeting):
        if meeting.ingress_http:
            return meeting.ingress_http.uri

        default_uri = 'https://{hostname}'.format(**self.context)
        port = self.context.get('port')
        if port:
            default_uri += ':{}'.format(port)
        return default_uri

    def _guest_sip_authorization(self, model):
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

        return b64encode('{}:{}'.format(username, password).encode()).decode()
