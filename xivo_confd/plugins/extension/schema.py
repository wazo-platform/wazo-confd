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
from marshmallow.class_registry import register

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink

EXTEN_REGEX = r'^_[*#0-9_XxZzNn\[\].!-]{1,39}$|[*#0-9]{1,40}$'


class ExtensionSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    exten = fields.String(validate=Regexp(EXTEN_REGEX), required=True)
    context = fields.String(required=True)
    commented = fields.Boolean(attribute='legacy_commented')
    links = ListLink(Link('extensions'))
    incall = fields.Nested('IncallSchema',
                           only=['id', 'links'],
                           dump_only=True)

register('ExtensionSchema', ExtensionSchema)
