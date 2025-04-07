# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from xivo_dao.alchemy.parking_lot import ParkingLot

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import ParkingLotSchema


class ParkingLotList(ListResource):
    model = ParkingLot
    schema = ParkingLotSchema

    def build_headers(self, parking_lot):
        return {'Location': url_for('parkinglots', id=parking_lot.id, _external=True)}

    @required_acl('confd.parkinglots.create')
    def post(self):
        return super().post()

    @required_acl('confd.parkinglots.read')
    def get(self):
        return super().get()


class ParkingLotItem(ItemResource):
    schema = ParkingLotSchema
    has_tenant_uuid = True

    @required_acl('confd.parkinglots.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.parkinglots.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.parkinglots.{id}.delete')
    def delete(self, id):
        return super().delete(id)
