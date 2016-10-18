# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import re
import string

from marshmallow import fields
from marshmallow.validate import Length, Regexp, OneOf

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

USERNAME_REGEX = r"^[a-zA-Z0-9_-]{1,40}$"
SECRET_REGEX = r"^[{}]{{1,80}}$".format(re.escape(string.printable))


class SipSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
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
