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


IP_REGEX = r'(1?\d{1,2}|2([0-4][0-9]|5[0-5]))(\.(1?\d{1,2}|2([0-4][0-9]|5[0-5]))){3}$'
MAC_REGEX = r'^([0-9A-Fa-f]{2})(:[0-9A-Fa-f]{2}){5}$'


class DeviceOptionsSchema(BaseSchema):
    switchboard = StrictBoolean()


class DeviceSchema(BaseSchema):
    id = fields.String(dump_only=True)
    status = fields.String(dump_only=True)

    ip = fields.String(validate=Regexp(IP_REGEX), allow_none=True)
    mac = fields.String(validate=Regexp(MAC_REGEX), allow_none=True)
    sn = fields.String(allow_none=True)
    plugin = fields.String(allow_none=True)
    vendor = fields.String(allow_none=True)
    model = fields.String(allow_none=True)
    version = fields.String(allow_none=True)
    description = fields.String(allow_none=True)
    template_id = fields.String(allow_none=True)
    options = fields.Nested(DeviceOptionsSchema, allow_none=True)
    links = ListLink(Link('devices'))
