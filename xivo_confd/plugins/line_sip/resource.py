# -*- coding: UTF-8 -*-

# Copyright (C) 2015 Avencall
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

from flask_restful import reqparse, inputs, fields

from xivo_confd.helpers.restful import FieldList, Link, DigitStr, \
    ListResource, ItemResource
from xivo_confd.plugins.line_sip.model import LineSip


fields = {
    'id': fields.Integer,
    'username': fields.String,
    'secret': fields.String,
    'callerid': fields.String,
    'device_slot': fields.Integer,
    'context': fields.String,
    'provisioning_extension': fields.String,
    'links': FieldList(Link('lines'))
}


parser = reqparse.RequestParser()
parser.add_argument('username',
                    type=inputs.regex(r"^[a-zA-Z0-9]+$"),
                    store_missing=False)
parser.add_argument('secret',
                    type=inputs.regex(r"^[a-zA-Z0-9]+$"),
                    store_missing=False)
parser.add_argument('context', required=True)
parser.add_argument('provisioning_extension',
                    type=DigitStr(6),
                    store_missing=False)
parser.add_argument('device_slot',
                    type=inputs.positive,
                    default=1)
parser.add_argument('callerid',
                    type=inputs.regex(r'"[^"]+"(\s+<[+0-9]>)?'),
                    store_missing=False)


class LineSipList(ListResource):

    model = LineSip
    fields = fields
    parser = parser


class LineSipItem(ItemResource):

    fields = fields
    parser = parser.copy()
    parser.replace_argument('context', store_missing=False)
