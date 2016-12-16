# -*- coding: utf-8 -*-

# Copyright (C) 2016 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

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
