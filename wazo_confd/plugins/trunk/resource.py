# Copyright 2016-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import TrunkSchema


class TrunkList(ListResource):

    model = Trunk
    schema = TrunkSchema

    def build_headers(self, trunk):
        return {'Location': url_for('trunks', id=trunk.id, _external=True)}

    @required_acl('confd.trunks.create')
    def post(self):
        return super().post()

    @required_acl('confd.trunks.read')
    def get(self):
        return super().get()


class TrunkItem(ItemResource):

    schema = TrunkSchema
    has_tenant_uuid = True

    @required_acl('confd.trunks.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.trunks.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.trunks.{id}.delete')
    def delete(self, id):
        return super().delete(id)
