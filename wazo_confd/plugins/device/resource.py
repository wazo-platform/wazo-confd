# Copyright 2016-2024 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from wazo.tenant_flask_helpers import Tenant

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import (
    ListResource,
    ItemResource,
    ConfdResource,
    build_tenant,
)
from wazo_confd.plugins.device.model import Device

from .schema import DeviceSchema


class SingleTenantMixin:
    def _add_tenant_uuid(self):
        tenant_uuid = Tenant.autodetect().uuid
        return {'tenant_uuid': tenant_uuid}


class SingleTenantConfdResource(SingleTenantMixin, ConfdResource):
    pass


class DeviceList(SingleTenantMixin, ListResource):
    model = Device.from_args
    schema = DeviceSchema

    def build_headers(self, device):
        return {'Location': url_for('devices', id=device.id, _external=True)}

    @required_acl('confd.devices.read')
    def get(self):
        params = self.search_params()
        kwargs = self._add_tenant_uuid()
        total, items = self.service.search(params, **kwargs)
        return {'total': total, 'items': self.schema().dump(items, many=True)}

    @required_acl('confd.devices.create')
    def post(self):
        form = self.schema().load(request.get_json())
        model = self.model(**form)
        kwargs = self._add_tenant_uuid()
        model = self.service.create(model, **kwargs)
        return self.schema().dump(model), 201, self.build_headers(model)


class UnallocatedDeviceList(ListResource):
    model = Device.from_args
    schema = DeviceSchema

    @required_acl('confd.devices.unallocated.read')
    def get(self):
        params = self.search_params()
        params['recurse'] = False

        total, items = self.service.search(params)
        return {'total': total, 'items': self.schema().dump(items, many=True)}


class UnallocatedDeviceItem(SingleTenantConfdResource):
    def __init__(self, middleware):
        self._middleware = middleware

    @required_acl('confd.devices.unallocated.{id}.update')
    def put(self, id):
        tenant_uuid = build_tenant()
        self._middleware.assign_tenant(id, tenant_uuid)
        return '', 204


class DeviceItem(SingleTenantMixin, ItemResource):
    schema = DeviceSchema

    def __init__(self, service, middleware):
        super().__init__(service)
        self._middleware = middleware

    @required_acl('confd.devices.{id}.read')
    def get(self, id):
        tenant_uuid = build_tenant()
        return self._middleware.get(id, tenant_uuid)

    @required_acl('confd.devices.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.devices.{id}.delete')
    def delete(self, id):
        return super().delete(id)


class DeviceAutoprov(SingleTenantConfdResource):
    def __init__(self, middleware):
        self._middleware = middleware

    @required_acl('confd.devices.{id}.autoprov.read')
    def get(self, id):
        tenant_uuid = build_tenant()
        self._middleware.reset_autoprov(id, tenant_uuid)
        return ('', 204)


class DeviceSynchronize(SingleTenantConfdResource):
    def __init__(self, service):
        self.service = service

    @required_acl('confd.devices.{id}.synchronize.read')
    def get(self, id):
        kwargs = self._add_tenant_uuid()
        device = self.service.get(id, **kwargs)
        self.service.synchronize(device, tenant_uuid=kwargs['tenant_uuid'])
        return ('', 204)
