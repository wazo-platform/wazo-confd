# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from xivo_dao.alchemy.paging import Paging

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import PagingSchema


class PagingList(ListResource):
    model = Paging
    schema = PagingSchema

    def build_headers(self, paging):
        return {'Location': url_for('pagings', id=paging.id, _external=True)}

    @required_acl('confd.pagings.create')
    def post(self):
        return super().post()

    @required_acl('confd.pagings.read')
    def get(self):
        return super().get()


class PagingItem(ItemResource):
    schema = PagingSchema
    has_tenant_uuid = True

    @required_acl('confd.pagings.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.pagings.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.pagings.{id}.delete')
    def delete(self, id):
        return super().delete(id)
