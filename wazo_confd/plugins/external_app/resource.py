# Copyright 2020-2023 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for, request

from xivo.tenant_flask_helpers import Tenant
from xivo_dao import tenant_dao
from xivo_dao.alchemy.external_app import ExternalApp

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import ExternalAppSchema, ExternalAppNameSchema


class ExternalAppList(ListResource):
    schema = ExternalAppSchema
    has_tenant_uuid = True

    @required_acl('confd.external.apps.read')
    def get(self):
        return super().get()

    def post(self):
        return '', 405


class ExternalAppItem(ItemResource):
    schema = ExternalAppSchema
    name_schema = ExternalAppNameSchema
    model = ExternalApp
    has_tenant_uuid = True

    def build_headers(self, app):
        return {'Location': url_for('external_apps', name=app.name, _external=True)}

    def add_tenant_to_form(self, form):
        tenant = Tenant.autodetect()
        tenant_dao.find_or_create_tenant(tenant.uuid)
        form['tenant_uuid'] = tenant.uuid
        return form

    @required_acl('confd.external.apps.{name}.create')
    def post(self, name):
        body = request.get_json()
        form_part = self.name_schema().load({'name': name})
        form = self.schema().load(body)
        form = self.add_tenant_to_form(form)
        form.update(form_part)
        model = self.model(**form)
        model = self.service.create(model)
        return self.schema().dump(model), 201, self.build_headers(model)

    @required_acl('confd.external.apps.{name}.read')
    def get(self, name):
        return super().get(name)

    @required_acl('confd.external.apps.{name}.update')
    def put(self, name):
        return super().put(name)

    @required_acl('confd.external.apps.{name}.delete')
    def delete(self, name):
        return super().delete(name)

    def _add_tenant_uuid(self):
        # NOTE(fblackburn): Do not cross tenant when name is an identifier
        tenant_uuids = self._build_tenant_list({'recurse': False})
        return {'tenant_uuids': tenant_uuids}
