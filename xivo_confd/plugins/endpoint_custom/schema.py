# -*- coding: UTF-8 -*-

# Copyright (C) 2016 Avencall
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

from marshmallow import fields
from marshmallow.validate import Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean

INTERFACE_REGEX = r"^[a-zA-Z0-9#*./_@:-]{1,128}$"


class CustomSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    interface = fields.String(validate=Regexp(INTERFACE_REGEX), required=True)
    enabled = StrictBoolean()
    links = ListLink(Link('endpoint_custom'))
    trunk = fields.Nested('TrunkSchema', only=['links'], dump_only=True)
