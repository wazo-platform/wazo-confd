# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from marshmallow import fields

from xivo.tenant_flask_helpers import Tenant

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Link, ListLink
from wazo_confd.helpers.restful import ConfdResource


class LineDeviceSchema(BaseSchema):
    line_id = fields.Integer()
    device_id = fields.String()
    links = ListLink(
        Link('lines', field='line_id', target='id'),
        Link('devices', field='device_id', target='id'),
    )


class LineDevice(ConfdResource):
    def __init__(self, line_dao, device_dao, service):
        super().__init__()
        self.line_dao = line_dao
        self.device_dao = device_dao
        self.service = service


class LineDeviceAssociation(LineDevice):

    has_tenant_uuid = True

    @required_acl('confd.lines.{line_id}.devices.{device_id}.update')
    def put(self, line_id, device_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        tenant_uuid = Tenant.autodetect().uuid
        device = self.device_dao.get(device_id, tenant_uuid=tenant_uuid)
        self.service.associate(line, device)
        return '', 204

    @required_acl('confd.lines.{line_id}.devices.{device_id}.delete')
    def delete(self, line_id, device_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        tenant_uuid = Tenant.autodetect().uuid
        device = self.device_dao.get(device_id, tenant_uuid=tenant_uuid)
        self.service.dissociate(line, device)
        return '', 204


class LineDeviceGet(LineDevice):

    schema = LineDeviceSchema
    has_tenant_uuid = True

    @required_acl('confd.lines.{line_id}.devices.read')
    def get(self, line_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        line = self.line_dao.get(line_id, tenant_uuids=tenant_uuids)
        line_device = self.service.get_association_from_line(line)
        return self.schema().dump(line_device)


class DeviceLineGet(LineDevice):

    schema = LineDeviceSchema

    @required_acl('confd.devices.{device_id}.lines.read')
    def get(self, device_id):
        tenant_uuid = Tenant.autodetect().uuid
        device = self.device_dao.get(device_id, tenant_uuid=tenant_uuid)
        line_devices = self.service.find_all_associations_from_device(device)
        return {
            'total': len(line_devices),
            'items': self.schema().dump(line_devices, many=True),
        }
