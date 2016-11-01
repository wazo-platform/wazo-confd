# -*- coding: utf-8 -*-

# Copyright (C) 2016 Proformatique Inc.
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

from flask import url_for

from xivo_dao.alchemy.context import Context

from .schema import ContextSchema, ContextSchemaPUT
from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource


class ContextList(ListResource):

    model = Context
    schema = ContextSchema

    def build_headers(self, context):
        return {'Location': url_for('contexts', id=context.id, _external=True)}

    @required_acl('confd.contexts.create')
    def post(self):
        return super(ContextList, self).post()

    @required_acl('confd.contexts.read')
    def get(self):
        return super(ContextList, self).get()


class ContextItem(ItemResource):

    schema = ContextSchemaPUT

    @required_acl('confd.contexts.{id}.read')
    def get(self, id):
        return super(ContextItem, self).get(id)

    @required_acl('confd.contexts.{id}.update')
    def put(self, id):
        return super(ContextItem, self).put(id)

    @required_acl('confd.contexts.{id}.delete')
    def delete(self, id):
        return super(ContextItem, self).delete(id)
