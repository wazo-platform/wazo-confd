# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import url_for
from marshmallow import fields

from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from xivo_confd.helpers.restful import ListResource, ItemResource


class TrunkSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    tenant_uuid = fields.String(dump_only=True)
    context = fields.String(allow_none=True)
    twilio_incoming = StrictBoolean(allow_none=True)
    links = ListLink(Link('trunks'))

    endpoint_sip = fields.Nested('SipSchema', only=['id', 'username', 'links'], dump_only=True)
    endpoint_custom = fields.Nested('CustomSchema', only=['id', 'interface', 'links'], dump_only=True)
    endpoint_iax = fields.Nested('IAXSchema', only=['id', 'name', 'links'], dump_only=True)
    outcalls = fields.Nested('OutcallSchema', only=['id', 'name', 'links'], many=True, dump_only=True)
    register_iax = fields.Nested('RegisterIAXSchema', only=['id', 'links'], dump_only=True)
    register_sip = fields.Nested('RegisterSIPSchema', only=['id', 'links'], dump_only=True)


class TrunkList(ListResource):

    model = Trunk
    schema = TrunkSchema

    def build_headers(self, trunk):
        return {'Location': url_for('trunks', id=trunk.id, _external=True)}

    @required_acl('confd.trunks.create')
    def post(self):
        return super(TrunkList, self).post()

    @required_acl('confd.trunks.read')
    def get(self):
        return super(TrunkList, self).get()


class TrunkItem(ItemResource):

    schema = TrunkSchema
    has_tenant_uuid = True

    @required_acl('confd.trunks.{id}.read')
    def get(self, id):
        return super(TrunkItem, self).get(id)

    @required_acl('confd.trunks.{id}.update')
    def put(self, id):
        return super(TrunkItem, self).put(id)

    @required_acl('confd.trunks.{id}.delete')
    def delete(self, id):
        return super(TrunkItem, self).delete(id)
