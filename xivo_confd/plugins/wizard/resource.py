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

from flask_restful import reqparse, fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import FieldList, ItemResource, Strict


wizard_fields = {
    'license': fields.Boolean,
    'hostname': fields.String,
    'timezone': fields.String,
    'lang': fields.String,
    'password': fields.String
}

parser = reqparse.RequestParser()
parser.add_argument('license', type=bool, required=True)
parser.add_argument('hostname', type=Strict(unicode), required=True)
parser.add_argument('timezone', type=Strict(unicode), required=True)
parser.add_argument('lang', type=Strict(unicode), required=True)
parser.add_argument('password', type=Strict(unicode), required=True)


class WizardItem(ItemResource):

    fields = wizard_fields
    parser = parser

    def post(self):
        return super(WizardItem, self).post()

    @required_acl('confd.wizard.reset')
    def delete(self):
        return super(WizardItem, self).delete()
