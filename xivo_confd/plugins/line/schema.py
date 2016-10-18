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

from marshmallow import fields
from marshmallow.validate import Length, Predicate, Range

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink


class LineSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(dump_only=True)
    protocol = fields.String(dump_only=True)
    device_id = fields.String(dump_only=True)
    device_slot = fields.Integer(dump_only=True)
    provisioning_extension = fields.String(dump_only=True)

    context = fields.String(required=True)
    provisioning_code = fields.String(validate=(Predicate('isdigit'), Length(equal=6)))
    position = fields.Integer(validate=Range(min=1))
    caller_id_name = fields.String(allow_none=True)  # Validate length callerid_name + num = max(160)
    caller_id_num = fields.String(validate=Predicate('isdigit'), allow_none=True)
    registrar = fields.String(validate=Length(max=128))
    links = ListLink(Link('lines'))

    endpoint_sip = fields.Nested('SipSchema', only=['id', 'username', 'links'], dump_only=True)
    endpoint_sccp = fields.Nested('SccpSchema', only=['id', 'links'], dump_only=True)
    endpoint_custom = fields.Nested('CustomSchema', only=['id', 'interface', 'links'], dump_only=True)


class LineSchemaNullable(LineSchema):

    def on_bind_field(self, field_name, field_obj):
        super(LineSchemaNullable, self).on_bind_field(field_name, field_obj)
        nullable_fields = ['provisioning_code', 'position', 'registrar']
        if field_name in nullable_fields:
            field_obj.allow_none = True
