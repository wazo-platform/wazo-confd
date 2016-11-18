# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
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

from xivo_dao.alchemy.outcall import Outcall

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import OutcallSchema


class OutcallList(ListResource):

    model = Outcall
    schema = OutcallSchema

    def build_headers(self, outcall):
        return {'Location': url_for('outcalls', id=outcall.id, _external=True)}

    @required_acl('confd.outcalls.create')
    def post(self):
        return super(OutcallList, self).post()

    @required_acl('confd.outcalls.read')
    def get(self):
        return super(OutcallList, self).get()


class OutcallItem(ItemResource):

    schema = OutcallSchema

    @required_acl('confd.outcalls.{id}.read')
    def get(self, id):
        return super(OutcallItem, self).get(id)

    @required_acl('confd.outcalls.{id}.update')
    def put(self, id):
        return super(OutcallItem, self).put(id)

    @required_acl('confd.outcalls.{id}.delete')
    def delete(self, id):
        return super(OutcallItem, self).delete(id)
