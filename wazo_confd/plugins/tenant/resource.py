# Copyright 2020-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from xivo_dao.alchemy.tenant import Tenant

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import TenantSchema


class TenantList(ListResource):
    model = Tenant
    schema = TenantSchema
    has_tenant_uuid = True

    def build_headers(self, tenant):
        return {'Location': url_for('tenants', uuid=tenant.uuid, _external=True)}

    @required_acl('confd.tenants.read')
    def get(self):
        return super().get()


class TenantItem(ItemResource):
    schema = TenantSchema
    has_tenant_uuid = True

    @required_acl('confd.tenants.{uuid}.read')
    def get(self, uuid):
        return super().get(str(uuid))
