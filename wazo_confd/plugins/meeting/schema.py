# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from base64 import b64encode
from marshmallow import fields, pre_dump
from marshmallow.validate import Length

from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink


class MeetingSchema(BaseSchema):
    uuid = fields.UUID(dump_only=True)
    owner_uuids = fields.List(fields.UUID())
    name = fields.String(validate=Length(max=512), required=True)
    hostname = fields.Method('_hostname')
    port = fields.Method('_port')
    guest_sip_authorization = fields.String(dump_only=True)
    links = ListLink(Link('meetings', field='uuid'))
    tenant_uuid = fields.String(dump_only=True)

    def _hostname(self, *args):
        return self.context['hostname']

    def _port(self, *args):
        return self.context['port']

    @pre_dump
    def add_guest_sip_authorization(self, data):
        endpoint_sip = data.guest_endpoint_sip
        if not endpoint_sip:
            return data

        username = None
        password = None
        for option, value in endpoint_sip.auth_section_options:
            if option == 'username':
                username = value
            elif option == 'password':
                password = value

        data.guest_sip_authorization = b64encode(
            '{}:{}'.format(username, password).encode()
        )
        return data
