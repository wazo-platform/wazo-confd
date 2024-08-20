# Copyright 2020-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from wazo.tenant_flask_helpers import Tenant
from xivo_dao import tenant_dao
from xivo_dao.alchemy.user_external_app import UserExternalApp

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import (
    GETQueryStringSchema,
    UserExternalAppNameSchema,
    UserExternalAppSchema,
)


class UserExternalAppList(ListResource):
    schema = UserExternalAppSchema
    has_tenant_uuid = True

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    @required_acl('confd.users.{user_uuid}.external.apps.read')
    def get(self, user_uuid):
        params = self.search_params()
        params.update(GETQueryStringSchema().load(request.args))
        tenant_uuids = self._build_tenant_list({'recurse': True})
        user = self.user_dao.get_by_id_uuid(user_uuid, tenant_uuids=tenant_uuids)
        total, items = self.service.search(user.uuid, user.tenant_uuid, params)
        return {'total': total, 'items': self.schema().dump(items, many=True)}

    def post(self):
        return '', 405


class UserExternalAppItem(ItemResource):
    schema = UserExternalAppSchema
    name_schema = UserExternalAppNameSchema
    model = UserExternalApp
    has_tenant_uuid = True

    def __init__(self, service, user_dao):
        self.service = service
        self.user_dao = user_dao

    def build_headers(self, app):
        return {
            'Location': url_for(
                'user_external_apps',
                user_uuid=app.user_uuid,
                name=app.name,
                _external=True,
            )
        }

    def add_tenant_to_form(self, form):
        if not self._has_write_tenant_uuid():
            return form

        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        form['tenant_uuid'] = tenant.uuid
        return form

    @required_acl('confd.users.{user_uuid}.external.apps.{name}.create')
    def post(self, user_uuid, name):
        kwargs = self._add_tenant_uuid()
        user = self.user_dao.get_by_id_uuid(user_uuid, **kwargs)
        body = request.get_json()
        form_part = self.name_schema().load({'name': name})
        form = self.schema().load(body)
        form = self.add_tenant_to_form(form)
        form['user_uuid'] = user.uuid
        form.update(form_part)
        model = self.model(**form)
        model = self.service.create(model, user.tenant_uuid)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.users.{user_uuid}.external.apps.{name}.read')
    def get(self, user_uuid, name):
        kwargs = self._add_tenant_uuid()
        user = self.user_dao.get_by_id_uuid(user_uuid, **kwargs)
        view = GETQueryStringSchema().load(request.args)['view']
        model = self.service.get(user.uuid, user.tenant_uuid, name, view)
        return self.schema().dump(model)

    @required_acl('confd.users.{user_uuid}.external.apps.{name}.update')
    def put(self, user_uuid, name):
        kwargs = self._add_tenant_uuid()
        user = self.user_dao.get_by_id_uuid(user_uuid, **kwargs)
        model = self.service.get(user.uuid, user.tenant_uuid, name)
        self.parse_and_update(model, tenant_uuid=user.tenant_uuid)
        return '', 204

    @required_acl('confd.users.{user_uuid}.external.apps.{name}.delete')
    def delete(self, user_uuid, name):
        kwargs = self._add_tenant_uuid()
        user = self.user_dao.get_by_id_uuid(user_uuid, **kwargs)
        model = self.service.get(user.uuid, user.tenant_uuid, name)
        self.service.delete(model, user.tenant_uuid)
        return '', 204
