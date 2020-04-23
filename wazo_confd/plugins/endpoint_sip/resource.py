# Copyright 2015-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for

from xivo_dao.alchemy.endpoint_sip import EndpointSIP

from wazo_confd.auth import required_acl
from wazo_confd.helpers.restful import ListResource, ItemResource

from .schema import EndpointSIPSchema


class SipList(ListResource):

    model = EndpointSIP
    schema = EndpointSIPSchema

    def build_headers(self, sip):
        return {'Location': url_for('endpoint_sip', uuid=sip.uuid, _external=True)}

    @required_acl('confd.endpoints.sip.read')
    def get(self):
        return super(SipList, self).get()

    @required_acl('confd.endpoints.sip.create')
    def post(self):
        return super(SipList, self).post()


class SipItem(ItemResource):

    schema = EndpointSIPSchema
    has_tenant_uuid = True

    @required_acl('confd.endpoints.sip.{uuid}.read')
    def get(self, uuid):
        return super(SipItem, self).get(uuid)

    @required_acl('confd.endpoints.sip.{uuid}.update')
    def put(self, uuid):
        return super(SipItem, self).put(uuid)

    @required_acl('confd.endpoints.sip.{uuid}.delete')
    def delete(self, uuid):
        return super(SipItem, self).delete(uuid)
