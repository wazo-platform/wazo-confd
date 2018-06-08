# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from marshmallow import fields

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class TrunkSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class TrunksSchema(BaseSchema):
    trunks = fields.Nested(TrunkSchemaIDLoad, many=True, required=True)


class OutcallTrunkList(ConfdResource):

    schema = TrunksSchema

    def __init__(self, service, outcall_dao, trunk_dao):
        super(OutcallTrunkList, self).__init__()
        self.service = service
        self.outcall_dao = outcall_dao
        self.trunk_dao = trunk_dao

    @required_acl('confd.outcalls.{outcall_id}.trunks.update')
    def put(self, outcall_id):
        outcall = self.outcall_dao.get(outcall_id)
        form = self.schema().load(request.get_json()).data
        try:
            trunks = [self.trunk_dao.get(ot['id']) for ot in form['trunks']]
        except NotFoundError as e:
            raise errors.param_not_found('trunks', 'Trunk', **e.metadata)

        self.service.associate_all_trunks(outcall, trunks)

        return '', 204
