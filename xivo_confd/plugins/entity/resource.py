# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
#
# SPDX-License-Identifier: GPL-3.0+

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

    schema = EntitySchema
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

    schema = EntitySchema

    @required_acl('confd.entities.{id}.read')
    def get(self, id):
        return super(EntityItem, self).get(id)

    @required_acl('confd.entities.{id}.delete')
    def delete(self, id):
        return super(EntityItem, self).delete(id)

    def put(self, id):
        return '', 405
