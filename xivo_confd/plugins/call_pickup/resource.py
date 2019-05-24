# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.pickup import Pickup as CallPickup

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

from .schema import CallPickupSchema


class CallPickupList(ListResource):

    model = CallPickup
    schema = CallPickupSchema

    def build_headers(self, call_pickup):
        return {'Location': url_for('callpickups', id=call_pickup.id, _external=True)}

    @required_acl('confd.callpickups.create')
    def post(self):
        return super(CallPickupList, self).post()

    @required_acl('confd.callpickups.read')
    def get(self):
        return super(CallPickupList, self).get()


class CallPickupItem(ItemResource):

    schema = CallPickupSchema
    has_tenant_uuid = True

    @required_acl('confd.callpickups.{id}.read')
    def get(self, id):
        return super(CallPickupItem, self).get(id)

    @required_acl('confd.callpickups.{id}.update')
    def put(self, id):
        return super(CallPickupItem, self).put(id)

    @required_acl('confd.callpickups.{id}.delete')
    def delete(self, id):
        return super(CallPickupItem, self).delete(id)
