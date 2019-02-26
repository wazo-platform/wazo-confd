# -*- coding: utf-8 -*-
# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request, url_for
from xivo.tenant_flask_helpers import Tenant

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource, ConfdResource
from xivo_confd.plugins.device.model import Device

from .schema import DeviceSchema


class SingleTenantListResource(ListResource):

    def get(self):
        params = self.search_params()
        tenant_uuid = Tenant.autodetect().uuid

        kwargs = {}
        if tenant_uuid is not None:
            kwargs['tenant_uuid'] = tenant_uuid

        total, items = self.service.search(params, tenant_uuid=tenant_uuid)
        return {'total': total,
                'items': self.schema().dump(items, many=True).data}

    def put(self, id):
        kwargs = self._add_tenant_uuid()
        model = self.service.get(id, tenant_uuid=kwargs['tenant_uuid'])
        self.parse_and_update(model, tenant_uuid=kwargs['tenant_uuid'])
        return '', 204

    def delete(self, id, **kwargs):
        if not kwargs:
            kwargs = self._add_tenant_uuid()
        model = self.service.get(id, tenant_uuid=kwargs['tenant_uuid'])
        self.service.delete(model, tenant_uuid=kwargs['tenant_uuid'])
        return '', 204

    def _add_tenant_uuid(self):
        tenant_uuid = Tenant.autodetect().uuid
        return {'tenant_uuid': tenant_uuid}


class SingleTenantItemResource(ItemResource):

    def _add_tenant_uuid(self):
        tenant_uuid = Tenant.autodetect().uuid
        return {'tenant_uuid': tenant_uuid}


class SingleTenantConfdResource(ConfdResource):

    def _add_tenant_uuid(self):
        tenant_uuid = Tenant.autodetect().uuid
        return {'tenant_uuid': tenant_uuid}


class DeviceList(SingleTenantListResource):

    model = Device.from_args
    schema = DeviceSchema

    def build_headers(self, device):
        return {'Location': url_for('devices', id=device.id, _external=True)}

    @required_acl('confd.devices.read')
    def get(self):
        return super(DeviceList, self).get()

    @required_acl('confd.devices.create')
    def post(self):
        form = self.schema().load(request.get_json()).data
        model = self.model(**form)
        kwargs = self._add_tenant_uuid()
        model = self.service.create(model, tenant_uuid=kwargs['tenant_uuid'])
        return self.schema().dump(model).data, 201, self.build_headers(model)


class DeviceItem(SingleTenantItemResource):

    schema = DeviceSchema

    @required_acl('confd.devices.{id}.read')
    def get(self, id):
        return super(DeviceItem, self).get(id)

    @required_acl('confd.devices.{id}.update')
    def put(self, id):
        return super(DeviceItem, self).put(id)

    @required_acl('confd.devices.{id}.delete')
    def delete(self, id):
        return super(DeviceItem, self).delete(id)


class DeviceAutoprov(SingleTenantConfdResource):

    def __init__(self, service):
        self.service = service

    @required_acl('confd.devices.{id}.autoprov.read')
    def get(self, id):
        kwargs = self._add_tenant_uuid()
        device = self.service.get(id, **kwargs)
        self.service.reset_autoprov(device, tenant_uuid=kwargs['tenant_uuid'])
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
