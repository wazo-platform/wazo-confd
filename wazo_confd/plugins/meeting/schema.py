# Copyright 2021 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
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
