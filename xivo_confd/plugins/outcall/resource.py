# -*- coding: utf-8 -*-

# Copyright (C) 2016 Avencall
# Copyright (C) 2016 Proformatique Inc.
#
# SPDX-License-Identifier: GPL-3.0+

from flask import url_for

from xivo_dao.alchemy.outcall import Outcall

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.restful import ListResource, ItemResource

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

    @required_acl('confd.outcalls.{id}.read')
    def get(self, id):
        return super(OutcallItem, self).get(id)

    @required_acl('confd.outcalls.{id}.update')
    def put(self, id):
        return super(OutcallItem, self).put(id)

    @required_acl('confd.outcalls.{id}.delete')
    def delete(self, id):
        return super(OutcallItem, self).delete(id)
