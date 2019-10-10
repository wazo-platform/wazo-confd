# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ConfdResource


class ParkingLotExtensionItem(ConfdResource):

    has_tenant_uuid = True

    def __init__(self, service, parking_lot_dao, extension_dao):
        super(ParkingLotExtensionItem, self).__init__()
        self.service = service
        self.parking_lot_dao = parking_lot_dao
        self.extension_dao = extension_dao

    @required_acl('confd.parkinglots.{parking_lot_id}.extensions.{extension_id}.delete')
    def delete(self, parking_lot_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        parking_lot = self.parking_lot_dao.get(
            parking_lot_id, tenant_uuids=tenant_uuids
        )
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)
        self.service.dissociate(parking_lot, extension)
        return '', 204

    @required_acl('confd.parkinglots.{parking_lot_id}.extensions.{extension_id}.update')
    def put(self, parking_lot_id, extension_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        parking_lot = self.parking_lot_dao.get(
            parking_lot_id, tenant_uuids=tenant_uuids
        )
        extension = self.extension_dao.get(extension_id, tenant_uuids=tenant_uuids)
        self.service.associate(parking_lot, extension)
        return '', 204
