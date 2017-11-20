# -*- coding: UTF-8 -*-
# Copyright (C) 2015-2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for
from marshmallow import fields
from marshmallow.validate import Length

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource
from xivo_dao.alchemy.sccpline import SCCPLine as SCCPEndpoint


class SccpSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    options = fields.List(fields.List(fields.String(), validate=Length(equal=2)))
    links = ListLink(Link('endpoint_sccp'))

    line = fields.Nested('LineSchema', only=['id', 'links'], dump_only=True)


class SccpList(ListResource):

    model = SCCPEndpoint
    schema = SccpSchema

    def build_headers(self, sccp):
        return {'Location': url_for('endpoint_sccp', id=sccp.id, _external=True)}

    @required_acl('confd.endpoints.sccp.read')
    def get(self):
        return super(SccpList, self).get()

    @required_acl('confd.endpoints.sccp.create')
    def post(self):
        return super(SccpList, self).post()


class SccpItem(ItemResource):

    schema = SccpSchema

    @required_acl('confd.endpoints.sccp.{id}.read')
    def get(self, id):
        return super(SccpItem, self).get(id)

    @required_acl('confd.endpoints.sccp.{id}.update')
    def put(self, id):
        return super(SccpItem, self).put(id)

    @required_acl('confd.endpoints.sccp.{id}.delete')
    def delete(self, id):
        return super(SccpItem, self).delete(id)
