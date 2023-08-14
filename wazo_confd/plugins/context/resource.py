# Copyright 2016-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from uuid import uuid4

from xivo_dao.alchemy.context import Context

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ContextSchema, ContextSchemaPUT


class ContextList(ListResource):
    model = Context
    schema = ContextSchema
    context_name_fmt = 'ctx-{tenant_slug}-{context_type}-{context_uuid}'

    def __init__(self, tenant_dao, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._tenant_dao = tenant_dao

    def build_headers(self, context):
        return {'Location': url_for('contexts', id=context.id, _external=True)}

    @required_acl('confd.contexts.create')
    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)

        tenant = self._tenant_dao.get(form['tenant_uuid'])
        form['uuid'] = uuid4()
        form['name'] = self.context_name_fmt.format(
            tenant_slug=tenant.slug,
            context_type=form['type'],
            context_uuid=form['uuid'],
        )
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.contexts.read')
    def get(self):
        return super().get()


class ContextItem(ItemResource):
    schema = ContextSchemaPUT
    has_tenant_uuid = True

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.contexts.{id}.read')
    def get(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        return self._middleware.get(id=id, tenant_uuids=tenant_uuids)

    @required_acl('confd.contexts.{id}.update')
    def put(self, id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        self._middleware.update(id, request.get_json(), tenant_uuids)
        return '', 204

    @required_acl('confd.contexts.{id}.delete')
    def delete(self, id):
        return super().delete(id)
