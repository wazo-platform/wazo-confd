# Copyright 2018-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.useriax import UserIAX as IAXEndpoint

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import IAXSchema


class IAXList(ListResource):

    model = IAXEndpoint
    schema = IAXSchema

    def build_headers(self, iax):
        return {'Location': url_for('endpoint_iax', id=iax.id, _external=True)}

    @required_acl('confd.endpoints.iax.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.iax.create')
    def post(self):
        return super().post()


class IAXItem(ItemResource):

    schema = IAXSchema
    has_tenant_uuid = True

    @required_acl('confd.endpoints.iax.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.endpoints.iax.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.endpoints.iax.{id}.delete')
    def delete(self, id):
        return super().delete(id)
