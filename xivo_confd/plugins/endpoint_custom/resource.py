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

from xivo_confd.helpers.restful import FieldList, Link, ListResource, ItemResource
from xivo_dao.alchemy.usercustom import UserCustom as Custom


custom_fields = {
    'id': fields.Integer,
    'interface': fields.String,
    'enabled': fields.Boolean,
    'links': FieldList(Link('endpoint_custom'))
}


class CustomList(ListResource):

    model = Custom
    fields = custom_fields

    parser = reqparse.RequestParser()
    parser.add_argument('interface', required=True)
    parser.add_argument('enabled', type=bool, default=True)

    def build_headers(self, custom):
        return {'Location': url_for('endpoint_custom', id=custom.id, _external=True)}


class CustomItem(ItemResource):

    fields = custom_fields

    parser = reqparse.RequestParser()
    parser.add_argument('interface', store_missing=False)
    parser.add_argument('enabled', type=bool, store_missing=False)
