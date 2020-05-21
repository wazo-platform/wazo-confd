# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.usercustom import UserCustom as Custom

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import CustomSchema


class CustomList(ListResource):

    model = Custom
    schema = CustomSchema

    def build_headers(self, custom):
        return {'Location': url_for('endpoint_custom', id=custom.id, _external=True)}

    @required_acl('confd.endpoints.custom.read')
    def get(self):
        return super().get()

    @required_acl('confd.endpoints.custom.create')
    def post(self):
        return super().post()


class CustomItem(ItemResource):

    schema = CustomSchema
    has_tenant_uuid = True

    @required_acl('confd.endpoints.custom.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.endpoints.custom.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.endpoints.custom.{id}.delete')
    def delete(self, id):
        return super().delete(id)
