# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class TrunkSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class TrunksSchema(BaseSchema):
    trunks = Nested(TrunkSchemaIDLoad, many=True, required=True)


class OutcallTrunkList(ConfdResource):
    schema = TrunksSchema
    has_tenant_uuid = True

    def __init__(self, service, outcall_dao, trunk_dao):
        super().__init__()
        self.service = service
        self.outcall_dao = outcall_dao
        self.trunk_dao = trunk_dao

    @required_acl('confd.outcalls.{outcall_id}.trunks.update')
    def put(self, outcall_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})
        outcall = self.outcall_dao.get(outcall_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json(force=True))
        try:
            trunks = [
                self.trunk_dao.get(trunk['id'], tenant_uuids=tenant_uuids)
                for trunk in form['trunks']
            ]
        except NotFoundError as e:
            raise errors.param_not_found('trunks', 'Trunk', **e.metadata)

        self.service.associate_all_trunks(outcall, trunks)

        return '', 204
