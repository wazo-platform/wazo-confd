# -*- coding: utf-8 -*-

# Copyright 2016 The Wazo Authors  (see the AUTHORS file)
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

from xivo_dao.alchemy.paging import Paging

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import PagingSchema


class PagingList(ListResource):

    model = Paging
    schema = PagingSchema

    def build_headers(self, paging):
        return {'Location': url_for('pagings', id=paging.id, _external=True)}

    @required_acl('confd.pagings.create')
    def post(self):
        return super(PagingList, self).post()

    @required_acl('confd.pagings.read')
    def get(self):
        return super(PagingList, self).get()


class PagingItem(ItemResource):

    schema = PagingSchema

    @required_acl('confd.pagings.{id}.read')
    def get(self, id):
        return super(PagingItem, self).get(id)

    @required_acl('confd.pagings.{id}.update')
    def put(self, id):
        return super(PagingItem, self).put(id)

    @required_acl('confd.pagings.{id}.delete')
    def delete(self, id):
        return super(PagingItem, self).delete(id)
