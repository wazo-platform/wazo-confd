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
from flask_restful import reqparse, inputs, fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, \
    option
from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint
from .validator import (NAME_REGEX as USERNAME_REGEX,
                        SECRET_REGEX)


sip_fields = {
    'id': fields.Integer,
    'username': fields.String(attribute='name'),
    'secret': fields.String,
    'type': fields.String,
    'host': fields.String,
    'options': fields.List(fields.List(fields.String)),
    'links': FieldList(Link('endpoint_sip'))
}

sip_parser = reqparse.RequestParser()
sip_parser.add_argument('username',
                        type=inputs.regex(USERNAME_REGEX),
                        dest='name',
                        store_missing=False)
sip_parser.add_argument('secret',
                        type=inputs.regex(SECRET_REGEX),
                        store_missing=False)
sip_parser.add_argument('type',
                        choices=('friend', 'peer', 'user'),
                        store_missing=False)
sip_parser.add_argument('host', store_missing=False)
sip_parser.add_argument('options',
                        action='append',
                        type=option,
                        store_missing=False,
                        nullable=False)


class SipList(ListResource):

    model = SIPEndpoint
    fields = sip_fields
    parser = sip_parser

    def build_headers(self, sip):
        return {'Location': url_for('endpoint_sip', id=sip.id, _external=True)}

    @required_acl('confd.endpoints.sip.read')
    def get(self):
        return super(SipList, self).get()

    @required_acl('confd.endpoints.sip.create')
    def post(self):
        return super(SipList, self).post()


class SipItem(ItemResource):

    fields = sip_fields
    parser = sip_parser

    @required_acl('confd.endpoints.sip.{id}.read')
    def get(self, id):
        return super(SipItem, self).get(id)

    @required_acl('confd.endpoints.sip.{id}.update')
    def put(self, id):
        return super(SipItem, self).put(id)

    @required_acl('confd.endpoints.sip.{id}.delete')
    def delete(self, id):
        return super(SipItem, self).delete(id)
