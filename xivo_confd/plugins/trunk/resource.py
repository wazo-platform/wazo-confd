# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink, StrictBoolean
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_dao.alchemy.trunkfeatures import TrunkFeatures as Trunk


class TrunkSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    context = fields.String(allow_none=True)
    twilio_incoming = StrictBoolean(allow_none=True)
    links = ListLink(Link('trunks'))
    endpoint_sip = fields.Nested('SipSchema', only=['id', 'username', 'links'], dump_only=True)
    endpoint_custom = fields.Nested('CustomSchema', only=['id', 'interface', 'links'], dump_only=True)
    outcalls = fields.Nested('OutcallSchema', only=['id', 'name', 'links'], many=True, dump_only=True)


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

    @required_acl('confd.trunks.{id}.read')
    def get(self, id):
        return super(TrunkItem, self).get(id)

    @required_acl('confd.trunks.{id}.update')
    def put(self, id):
        return super(TrunkItem, self).put(id)

    @required_acl('confd.trunks.{id}.delete')
    def delete(self, id):
        return super(TrunkItem, self).delete(id)
