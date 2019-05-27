# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import Length, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean

INTERFACE_REGEX = r"^[a-zA-Z0-9#*./_@:-]{1,128}$"


class CustomSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    interface = fields.String(validate=Regexp(INTERFACE_REGEX), required=True)
    interface_suffix = fields.String(validate=Length(max=32), allow_none=True)
    enabled = StrictBoolean()
    links = ListLink(Link('endpoint_custom'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)
