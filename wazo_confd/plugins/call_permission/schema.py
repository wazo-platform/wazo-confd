# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields
from marshmallow.validate import OneOf, Regexp

from wazo_confd.helpers.mallow import BaseSchema, StrictBoolean, Link, ListLink

NAME_REGEX = r'^[a-z0-9_-]{1,128}$'
PASSWORD_REGEX = r'^[0-9#\*]{1,40}$'
EXTENSION_REGEX = r'^(?:_?\+?[0-9NXZ\*#\-\[\]]+[\.\!]?){1,40}$'


class CallPermissionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    name = fields.String(validate=Regexp(NAME_REGEX), required=True)
    password = fields.String(validate=Regexp(PASSWORD_REGEX), allow_none=True)
    mode = fields.String(validate=OneOf(['allow', 'deny']))
    extensions = fields.List(fields.String(validate=Regexp(EXTENSION_REGEX)))
    enabled = StrictBoolean()
    description = fields.String(allow_none=True)
    links = ListLink(Link('callpermissions'))

    outcalls = fields.Nested(
        'OutcallSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    groups = fields.Nested(
        'GroupSchema', only=['id', 'name', 'links'], many=True, dump_only=True
    )
    users = fields.Nested(
        'UserSchema',
        only=['uuid', 'firstname', 'lastname', 'links'],
        many=True,
        dump_only=True,
    )
