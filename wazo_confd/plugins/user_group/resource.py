# Copyright 2017-2022 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import fields, validates_schema, post_load
from marshmallow.exceptions import ValidationError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema, Nested
from wazo_confd.helpers.restful import ConfdResource


class GroupSchemaIDUUIDLoad(BaseSchema):
    id = fields.Integer()
    uuid = fields.UUID()

    @validates_schema
    def _validate_at_least_one_identifier(self, data, **kwargs):
        _id = data.get('id')
        uuid = data.get('uuid')

        provided_identifiers = [identifier for identifier in [_id, uuid] if identifier]
        if len(provided_identifiers) == 0:
            raise ValidationError('One identifier(id or uuid) must be provided')

    @post_load
    def remove_identifier_not_provided(self, data, **kwargs):
        for k in ['id', 'uuid']:
            try:
                if not data[k]:
                    del data[k]
            except KeyError:
                pass
        return data


class GroupsIDUUIDSchema(BaseSchema):
    groups = Nested(GroupSchemaIDUUIDLoad, many=True, required=True)


class UserGroupItem(ConfdResource):

    schema = GroupsIDUUIDSchema

    def __init__(self, service, middleware):
        super().__init__()
        self.service = service
        self._middleware = middleware

    @required_acl('confd.users.{user_id}.groups.update')
    def put(self, user_id):
        self._middleware.associate_all_groups(request.get_json(), user_id)
        return '', 204
