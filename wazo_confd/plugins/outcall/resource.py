# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.outcall import Outcall

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

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
    has_tenant_uuid = True

    @required_acl('confd.outcalls.{id}.read')
    def get(self, id):
        return super(OutcallItem, self).get(id)

    @required_acl('confd.outcalls.{id}.update')
    def put(self, id):
        return super(OutcallItem, self).put(id)

    @required_acl('confd.outcalls.{id}.delete')
    def delete(self, id):
        return super(OutcallItem, self).delete(id)
