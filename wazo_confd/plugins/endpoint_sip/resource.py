# Copyright 2015-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.usersip import UserSIP as SIPEndpoint

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import SipSchema, SipSchemaNullable


class SipList(ListResource):

    model = SIPEndpoint
    schema = SipSchemaNullable

    def build_headers(self, sip):
        return {'Location': url_for('endpoint_sip', id=sip.id, _external=True)}

    @required_acl('confd.endpoints.sip.read')
    def get(self):
        return super(SipList, self).get()

    @required_acl('confd.endpoints.sip.create')
    def post(self):
        return super(SipList, self).post()


class SipItem(ItemResource):

    schema = SipSchema
    has_tenant_uuid = True

    @required_acl('confd.endpoints.sip.{id}.read')
    def get(self, id):
        return super(SipItem, self).get(id)

    @required_acl('confd.endpoints.sip.{id}.update')
    def put(self, id):
        return super(SipItem, self).put(id)

    @required_acl('confd.endpoints.sip.{id}.delete')
    def delete(self, id):
        return super(SipItem, self).delete(id)
