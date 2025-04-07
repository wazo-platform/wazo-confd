# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from xivo_dao.alchemy.ivr import IVR

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ItemResource, ListResource

from .schema import IvrSchema


class IvrList(ListResource):
    model = IVR
    schema = IvrSchema

    def build_headers(self, ivr):
        return {'Location': url_for('ivr', id=ivr.id, _external=True)}

    @required_acl('confd.ivr.create')
    def post(self):
        return super().post()

    @required_acl('confd.ivr.read')
    def get(self):
        return super().get()


class IvrItem(ItemResource):
    schema = IvrSchema
    has_tenant_uuid = True

    @required_acl('confd.ivr.{id}.read')
    def get(self, id):
        return super().get(id)

    @required_acl('confd.ivr.{id}.update')
    def put(self, id):
        return super().put(id)

    @required_acl('confd.ivr.{id}.delete')
    def delete(self, id):
        return super().delete(id)
