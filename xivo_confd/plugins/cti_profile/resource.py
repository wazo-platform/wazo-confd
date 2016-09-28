# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource


class CtiProfileSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    links = ListLink(Link('cti_profiles'))


class CtiProfileList(ListResource):

    schema = CtiProfileSchema

    @required_acl('confd.cti_profiles.read')
    def get(self):
        return super(CtiProfileList, self).get()

    def post(self):
        return '', 405


class CtiProfileItem(ItemResource):

    schema = CtiProfileSchema

    @required_acl('confd.cti_profiles.{id}.read')
    def get(self, id):
        return super(CtiProfileItem, self).get(id)

    def delete(self):
        return '', 405

    def put(self):
        return '', 405
