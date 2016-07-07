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

import re
from flask import url_for
from marshmallow import fields
from marshmallow.validate import Length, Regexp

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_dao.alchemy.entity import Entity

NAME_REGEX = re.compile(r'^[a-z0-9_\.-]{1,64}$')


class EntitySchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String(validate=Regexp(NAME_REGEX), required=True)
    display_name = fields.String(validate=Length(min=3, max=128), allow_none=True)
    description = fields.Constant('', load_only=True)  # Avoid mess with webi
    links = ListLink(Link('entities'))


class EntityList(ListResource):

    schema = EntitySchema()
    model = Entity

    def build_headers(self, entity):
        return {'Location': url_for('entities', id=entity.id, _external=True)}

    @required_acl('confd.entities.create')
    def post(self):
        return super(EntityList, self).post()

    @required_acl('confd.entities.read')
    def get(self):
        return super(EntityList, self).get()


class EntityItem(ItemResource):

    schema = EntitySchema()

    @required_acl('confd.entities.{id}.read')
    def get(self, id):
        return super(EntityItem, self).get(id)

    @required_acl('confd.entities.{id}.delete')
    def delete(self, id):
        return super(EntityItem, self).delete(id)

    def put(self, id):
        return '', 405
