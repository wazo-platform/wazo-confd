# Copyright 2015-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from flask_restful import Resource

import marshmallow

from wazo.flask.auth_verifier import AuthVerifierFlask
from wazo.mallow import fields, validate
from wazo.tenant_flask_helpers import Tenant, token
from xivo_dao import tenant_dao

from wazo_confd.helpers.common import handle_api_exception
from wazo_confd.helpers.mallow import BaseSchema

auth_verifier = AuthVerifierFlask()


class ErrorCatchingResource(Resource):
    method_decorators = [handle_api_exception] + Resource.method_decorators


class ListSchema(BaseSchema):
    limit = fields.Integer(validate=validate.Range(min=0))
    offset = fields.Integer(validate=validate.Range(min=0))
    search = fields.String()
    recurse = fields.Boolean()

    class Meta:
        unknown = marshmallow.INCLUDE


class ConfdResource(ErrorCatchingResource):
    method_decorators = [
        auth_verifier.verify_tenant,
        auth_verifier.verify_token,
    ] + ErrorCatchingResource.method_decorators

    def _has_write_tenant_uuid(self):
        return (
            self._has_write_tenant_uuid_sqlalchemy()
            or self._has_write_tenant_uuid_custom()
        )

    def _has_write_tenant_uuid_sqlalchemy(self):
        return (
            hasattr(self, 'model')
            and hasattr(self.model, '__mapper__')
            and hasattr(self.model.__mapper__.c, 'tenant_uuid')
        )

    def _has_write_tenant_uuid_custom(self):
        return hasattr(self, 'model') and hasattr(self.model, 'has_tenant_uuid')

    def _has_a_tenant_uuid(self):
        if getattr(self, 'has_tenant_uuid', None):
            return True

        return self._has_write_tenant_uuid()

    def _build_tenant_list(self, params):
        if not self._has_a_tenant_uuid():
            return

        tenant_uuid = Tenant.autodetect().uuid
        if not params.get('recurse', False):
            return [tenant_uuid]

        return [tenant.uuid for tenant in token.visible_tenants(tenant_uuid)]


class ListResource(ConfdResource):
    def __init__(self, service):
        super().__init__()
        self.service = service

    def get(self):
        params = self.search_params()
        tenant_uuids = self._build_tenant_list(params)
        kwargs = {}
        if tenant_uuids is not None:
            kwargs['tenant_uuids'] = tenant_uuids

        total, items = self.service.search(params, **kwargs)
        return {'total': total, 'items': self.schema().dump(items, many=True)}

    def search_params(self):
        return ListSchema().load(request.args)

    def add_tenant_to_form(self, form):
        if not self._has_write_tenant_uuid():
            return form

        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        form['tenant_uuid'] = tenant.uuid
        return form

    def post(self):
        form = self.schema().load(request.get_json())
        form = self.add_tenant_to_form(form)
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    def build_headers(self, model):
        raise NotImplementedError()


class ItemResource(ConfdResource):
    has_tenant_uuid = False

    def __init__(self, service):
        super().__init__()
        self.service = service

    def get(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        return self.schema().dump(model)

    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, **kwargs)
        self.parse_and_update(model)
        return '', 204

    def parse_and_update(self, model, **kwargs):
        form = self.schema().load(request.get_json(), partial=True)
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.items():
            setattr(model, name, value)
        self.service.edit(model, updated_fields=updated_fields, **kwargs)

    def find_updated_fields(self, model, form):
        updated_fields = []
        for name, value in form.items():
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

        tenant_uuids = self._build_tenant_list({'recurse': True})
        return {'tenant_uuids': tenant_uuids}


def build_tenant():
    tenant = Tenant.autodetect()
    tenant_dao.find_or_create_tenant(tenant.uuid)
    return tenant.uuid


def is_recursive():
    return request.args.get(
        'recursive', default=False, type=lambda v: v.lower() == 'true'
    )
