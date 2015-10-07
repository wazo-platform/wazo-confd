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

from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, \
    option_list
from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint


sip_fields = {
    'id': fields.Integer,
    'username': fields.String,
    'secret': fields.String,
    'type': fields.String,
    'host': fields.String,
    'options': fields.List(fields.List(fields.String)),
    'links': FieldList(Link('endpoint_sip'))
}

sip_parser = reqparse.RequestParser()
sip_parser.add_argument('username',
                        type=inputs.regex(r"^[a-zA-Z0-9]+$"),
                        store_missing=False)
sip_parser.add_argument('secret',
                        type=inputs.regex(r"^\w+$"),
                        store_missing=False)
sip_parser.add_argument('type', default='friend')
sip_parser.add_argument('host', default='dynamic')
sip_parser.add_argument('options',
                        type=option_list,
                        store_missing=False)


class SipList(ListResource):

    model = SIPEndpoint
    fields = sip_fields
    parser = sip_parser


class SipItem(ItemResource):

    fields = sip_fields
    parser = sip_parser
