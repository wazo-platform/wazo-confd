# Copyright 2018-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class ContextSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class ContextsSchema(BaseSchema):
    contexts = Nested(ContextSchemaIDLoad, many=True, required=True)


class ContextContextList(ConfdResource):
    schema = ContextsSchema

    def __init__(self, service, context_dao):
        super().__init__()
        self.service = service
        self.context_dao = context_dao

    @required_acl('confd.contexts.{context_id}.contexts.update')
    def put(self, context_id):
        context = self.context_dao.get(context_id)
        form = self.schema().load(request.get_json(force=True))
        try:
            contexts = [self.context_dao.get(c['id']) for c in form['contexts']]
        except NotFoundError as e:
            raise errors.param_not_found('contexts', 'Context', **e.metadata)

        self.service.associate_contexts(context, contexts)

        return '', 204
