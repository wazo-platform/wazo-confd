# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from flask_restful import Resource

from xivo.tenant_flask_helpers import get_auth_client, Tenant
from xivo_dao import tenant_dao
from xivo_dao.helpers import errors

from xivo_confd.auth import authentication
from xivo_confd.helpers.common import handle_api_exception


class ErrorCatchingResource(Resource):
    method_decorators = ([handle_api_exception] + Resource.method_decorators)


class ConfdResource(ErrorCatchingResource):
    method_decorators = [authentication.login_required] + ErrorCatchingResource.method_decorators


class ListResource(ConfdResource):

    def __init__(self, service):
        super(ListResource, self).__init__()
        self.service = service

    def get(self):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)

        kwargs = {}
        if tenant_uuids is not None:
            kwargs['tenant_uuids'] = tenant_uuids

        total, items = self.service.search(params, **kwargs)
        return {'total': total,
                'items': self.schema().dump(items, many=True).data}

    def search_params(self):
        args = ((key, request.args[key]) for key in request.args)
        params = {}

        for key, value in args:
            if key in ('limit', 'skip', 'offset'):
                params[key] = self.convert_numeric(key, value)
            elif key == 'recurse':
                params[key] = self.convert_boolean(key, value)
            else:
                params[key] = value

        return params

    def convert_boolean(self, key, value):
        true_values = ('true', 'True')
        return value in true_values

    def convert_numeric(self, key, value):
        if not value.isdigit():
            raise errors.wrong_type(key, "positive number")
        return int(value)

    def post(self):
        form = self.schema().load(request.get_json()).data

        if self._has_a_tenant_uuid():
            tenant = Tenant.autodetect()
            tenant_dao.get_or_create_tenant(tenant.uuid)
            form['tenant_uuid'] = tenant.uuid

        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    def build_headers(self, model):
        raise NotImplementedError()

    def _has_a_tenant_uuid(self):
        return (
            hasattr(self, 'model')
            and hasattr(self.model, '__mapper__')
            and hasattr(self.model.__mapper__.c, 'tenant_uuid')
        )

    def _build_tenant_list(self, params):
        if not self._has_a_tenant_uuid():
            return

        tenant = Tenant.autodetect().uuid
        recurse = params.get('recurse', False)
        if not recurse:
            return [tenant]

        tenants = []
        for tenant in get_auth_client().tenants.list(tenant_uuid=tenant)['items']:
            tenants.append(tenant['uuid'])
        return tenants


class ItemResource(ConfdResource):

    has_tenant_uuid = False

    def __init__(self, service):
        super(ItemResource, self).__init__()
        self.service = service

    def get(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        return self.schema().dump(model).data

    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model)
        return '', 204

    def parse_and_update(self, model):
        form = self.schema().load(request.get_json(), partial=True).data
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, updated_fields)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.iteritems():
            try:
                if getattr(model, name) != value:
                    updated_fields.append(name)
            except AttributeError:
                pass
        return updated_fields

    def delete(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.service.delete(model)
        return '', 204

    def _add_tenant_uuid(self):
        if not self.has_tenant_uuid:
            return {}

        tenant_uuids = [t.uuid for t in Tenant.autodetect(many=True)]
        return {'tenant_uuids': tenant_uuids}
