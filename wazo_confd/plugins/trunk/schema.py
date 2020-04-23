# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean


class TrunkSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    context = fields.String(allow_none=True)
    twilio_incoming = StrictBoolean(allow_none=True)
    links = ListLink(Link('trunks'))

    endpoint_sip = fields.Nested(
        'EndpointSIPSchema', only=['uuid', 'display_name', 'links'], dump_only=True
    )
    endpoint_custom = fields.Nested(
        'CustomSchema', only=['id', 'interface', 'links'], dump_only=True
    )
    endpoint_iax = fields.Nested(
        'IAXSchema', only=['id', 'name', 'links'], dump_only=True
    )
    outcalls = fields.Nested(
        'OutcallSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    register_iax = fields.Nested(
        'RegisterIAXSchema', only=['id', 'links'], dump_only=True
    )
    register_sip = fields.Nested(
        'RegisterSIPSchema', only=['id', 'links'], dump_only=True
    )
