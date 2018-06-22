# -*- coding: utf-8 -*-
# Copyright 2015-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

import logging

from flask import request
from flask_restful import Resource
from requests import HTTPError

from xivo.tenant_flask_helpers import get_auth_client, get_token, Tenant
from xivo_dao import tenant_dao
from xivo_dao.helpers import errors

from xivo_confd.auth import authentication
from xivo_confd.helpers.common import handle_api_exception

logger = logging.getLogger(__name__)


class ErrorCatchingResource(Resource):
    method_decorators = ([handle_api_exception] + Resource.method_decorators)


class ConfdResource(ErrorCatchingResource):

    method_decorators = [authentication.login_required] + ErrorCatchingResource.method_decorators

    def _has_a_tenant_uuid(self):
        if getattr(self, 'has_tenant_uuid', None):
            return True

        return (
            hasattr(self, 'model')
            and hasattr(self.model, '__mapper__')
            and hasattr(self.model.__mapper__.c, 'tenant_uuid')
        )

    def _build_tenant_list(self, params):
        # TODO remove all the logging in this function
        logger.debug('building tenant list: %s', params)
        if not self._has_a_tenant_uuid():
            logger.debug('does not have a tenant uuid')
            return

        logger.debug('headers: %s', request.headers)
        tenant = Tenant.autodetect().uuid
        logger.debug('%s detected', tenant)
        recurse = params.get('recurse', False)
        logger.debug('recurse: %s', recurse)
        if not recurse:
            logger.debug('no recurse [%s]', tenant)
            return [tenant]

        tenants = []
        auth_client = get_auth_client()
        token_data = get_token()
        logger.debug('using the following token: %s', token_data)
        auth_client.set_token(token_data['token'])

        try:
            tenants = auth_client.tenants.list(tenant_uuid=tenant)['items']
            logger.debug('found the following tenants: %s', tenants)
        except HTTPError as e:
            response = getattr(e, 'response', None)
            status_code = getattr(response, 'status_code', None)
            if status_code == 401:
                logger.debug('unauthorized returning [%s]', tenant)
                return [tenant]
            raise

        return [t['uuid'] for t in tenants]


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

    def parse_and_update(self, model, **kwargs):
        form = self.schema().load(request.get_json(), partial=True).data
        updated_fields = self.find_updated_fields(model, form)
        for name, value in form.iteritems():
            setattr(model, name, value)
        self.service.edit(model, updated_fields, **kwargs)

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

        tenant_uuids = self._build_tenant_list({'recurse': True})
        return {'tenant_uuids': tenant_uuids}
