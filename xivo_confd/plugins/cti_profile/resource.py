# -*- coding: utf-8 -*-
# Copyright (C) 2016 Avencall
# SPDX-License-Identifier: GPL-3.0+

from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema, Link, ListLink
from xivo_confd.helpers.restful import ListResource, ItemResource


class CtiProfileSchema(BaseSchema):
    id = fields.Integer(dump_only=True)
    name = fields.String()
    links = ListLink(Link('cti_profiles'))


class CtiProfileList(ListResource):

    schema = CtiProfileSchema

    @required_acl('confd.cti_profiles.read')
    def get(self):
        return super(CtiProfileList, self).get()

    def post(self):
        return '', 405


class CtiProfileItem(ItemResource):

    schema = CtiProfileSchema

    @required_acl('confd.cti_profiles.{id}.read')
    def get(self, id):
        return super(CtiProfileItem, self).get(id)

    def delete(self):
        return '', 405

    def put(self):
        return '', 405
