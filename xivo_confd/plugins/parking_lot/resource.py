# -*- coding: utf-8 -*-
# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

from xivo_dao.alchemy.parking_lot import ParkingLot

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import ParkingLotSchema


class ParkingLotList(ListResource):

    model = ParkingLot
    schema = ParkingLotSchema

    def build_headers(self, parking_lot):
        return {'Location': url_for('parkinglots', id=parking_lot.id, _external=True)}

    @required_acl('confd.parkinglots.create')
    def post(self):
        return super(ParkingLotList, self).post()

    @required_acl('confd.parkinglots.read')
    def get(self):
        return super(ParkingLotList, self).get()


class ParkingLotItem(ItemResource):

    schema = ParkingLotSchema

    @required_acl('confd.parkinglots.{id}.read')
    def get(self, id):
        return super(ParkingLotItem, self).get(id)

    @required_acl('confd.parkinglots.{id}.update')
    def put(self, id):
        return super(ParkingLotItem, self).put(id)

    @required_acl('confd.parkinglots.{id}.delete')
    def delete(self, id):
        return super(ParkingLotItem, self).delete(id)
