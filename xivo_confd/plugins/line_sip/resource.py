# -*- coding: UTF-8 -*-

# Copyright (C) 2015-2016 Avencall
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

from flask import url_for
from marshmallow import fields
from marshmallow.validate import Length, Predicate, Range, Regexp

from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_confd.plugins.line_sip.model import LineSip


USERNAME_REGEX = r'^[a-zA-Z0-9]+$'
SECRET_REGEX = r'^[a-zA-Z0-9]+$'
CALLERID_REGEX = r'"[^"]+"(\s+<[+0-9]>)?'


class LineSipSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    username = fields.String(validate=Regexp(USERNAME_REGEX))
    secret = fields.String(validate=Regexp(SECRET_REGEX))
    callerid = fields.String(validate=Regexp(CALLERID_REGEX), allow_none=True)
    device_slot = fields.Integer(validate=Range(min=0))
    context = fields.String(required=True)
    provisioning_extension = fields.String(validate=(Length(equal=6), Predicate('isdigit')))
    links = ListLink(Link('lines'),
                     Link('lines_sip'))


class LineSipList(ListResource):

    model = LineSip
    schema = LineSipSchema

    def build_headers(self, line):
        return {'Location': url_for('lines_sip', id=line.id, _external=True)}


class LineSipItem(ItemResource):

    schema = LineSipSchema
