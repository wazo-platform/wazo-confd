# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import re
import string

from marshmallow import fields
from marshmallow.validate import Length, Regexp, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

USERNAME_REGEX = r"^[a-zA-Z0-9_-]{1,40}$"
SECRET_REGEX = r"^[{}]{{1,80}}$".format(re.escape(string.printable))


class SipSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    username = fields.String(validate=Regexp(USERNAME_REGEX), attribute='name')
    secret = fields.String(validate=Regexp(SECRET_REGEX))
    type = fields.String(validate=OneOf(['friend', 'peer', 'user']))
    host = fields.String(validate=Length(max=255))
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('endpoint_sip'))

    trunk = fields.Nested('TrunkSchema', only=['id', 'links'], dump_only=True)
    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)


class SipSchemaNullable(SipSchema):

    def on_bind_field(self, field_name, field_obj):
        super(SipSchemaNullable, self).on_bind_field(field_name, field_obj)
        nullable_fields = ['username', 'host', 'secret']
        if field_name in nullable_fields:
            field_obj.allow_none = True
