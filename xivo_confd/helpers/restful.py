# -*- coding: UTF-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from flask_restful import Resource

from xivo.tenant_helpers import Tenant
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
        total, items = self.service.search(params)
        return {'total': total,
                'items': self.schema().dump(items, many=True).data}

    def search_params(self):
        args = ((key, request.args[key]) for key in request.args)
        params = {}

        for key, value in args:
            if key in ("limit", "skip", "offset"):
                params[key] = self.convert_numeric(key, value)
            else:
                params[key] = value

        return params

    def convert_numeric(self, key, value):
        if not value.isdigit():
            raise errors.wrong_type(key, "positive number")
        return int(value)

    def post(self):
        tenant = self._get_tenant()
        form = self.schema().load(request.get_json()).data
        if tenant:
            form['tenant_uuid'] = tenant.uuid

        tenant_uuid = form.get('tenant_uuid')
        if tenant_uuid:
            tenant_dao.get_or_create_tenant(tenant_uuid)

        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model).data, 201, self.build_headers(model)

    def build_headers(self, model):
        raise NotImplementedError()

    def _get_tenant(self):
        auth_token_cache = getattr(self, 'auth_token_cache', None)
        auth_user_cache = getattr(self, 'auth_user_cache', None)
        if auth_token_cache and auth_user_cache:
            return Tenant.autodetect(auth_token_cache, auth_user_cache)


class ItemResource(ConfdResource):

    def __init__(self, service):
        super(ItemResource, self).__init__()
        self.service = service

    def get(self, id):
        model = self.service.get(id)
        return self.schema().dump(model).data

    def put(self, id):
        model = self.service.get(id)
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
        model = self.service.get(id)
        self.service.delete(model)
        return '', 204
