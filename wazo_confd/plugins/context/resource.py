# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.context import Context

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ContextSchema, ContextSchemaPUT


class ContextList(ListResource):

    model = Context
    schema = ContextSchema

    def build_headers(self, context):
        return {'Location': url_for('contexts', id=context.id, _external=True)}

    @required_acl('confd.contexts.create')
    def post(self):
        return super().post()

    @required_acl('confd.contexts.read')
    def get(self):
        return super().get()


class ContextItem(ItemResource):

    schema = ContextSchemaPUT
    has_tenant_uuid = True

    @required_acl('confd.contexts.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.contexts.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.contexts.{id}.delete')
    def delete(self, id):
        return super().delete(id)
