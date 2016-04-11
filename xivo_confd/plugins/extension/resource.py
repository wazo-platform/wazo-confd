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

from flask import url_for
from flask_restful import reqparse, fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource, \
    Strict, DigitStr
from xivo_dao.alchemy.extension import Extension


fields = {
    'id': fields.Integer,
    'exten': fields.String,
    'context': fields.String,
    'commented': fields.Boolean(attribute='legacy_commented'),
    'links': FieldList(Link('extensions'))
}

parser = reqparse.RequestParser()
parser.add_argument('exten', type=DigitStr(), store_missing=False)
parser.add_argument('context', type=Strict(unicode), store_missing=False)
parser.add_argument('commented', type=Strict(bool), store_missing=False, dest='legacy_commented')


class ExtensionList(ListResource):

    model = Extension
    fields = fields
    parser = parser

    def build_headers(self, extension):
        return {'Location': url_for('extensions', id=extension.id, _external=True)}

    @required_acl('confd.extensions.read')
    def get(self):
        return super(ExtensionList, self).get()

    @required_acl('confd.extensions.create')
    def post(self):
        return super(ExtensionList, self).post()


class ExtensionItem(ItemResource):

    fields = fields
    parser = parser

    @required_acl('confd.extensions.{id}.read')
    def get(self, id):
        return super(ExtensionItem, self).get(id)

    @required_acl('confd.extensions.{id}.update')
    def put(self, id):
        return super(ExtensionItem, self).put(id)

    @required_acl('confd.extensions.{id}.delete')
    def delete(self, id):
        return super(ExtensionItem, self).delete(id)
