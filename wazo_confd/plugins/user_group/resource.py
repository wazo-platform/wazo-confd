# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request
from marshmallow import (
    EXCLUDE,
    fields,
)

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from wazo_confd.auth import required_acl
from wazo_confd.helpers.mallow import BaseSchema
from wazo_confd.helpers.restful import ConfdResource


class GroupSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class GroupsIDSchema(BaseSchema):
    groups = fields.Nested(
        GroupSchemaIDLoad,
        many=True, required=True, unknown=EXCLUDE
    )


class UserGroupItem(ConfdResource):

    schema = GroupsIDSchema

    def __init__(self, service, user_dao, group_dao):
        super(UserGroupItem, self).__init__()
        self.service = service
        self.user_dao = user_dao
        self.group_dao = group_dao

    @required_acl('confd.users.{user_id}.groups.update')
    def put(self, user_id):
        user = self.user_dao.get_by_id_uuid(user_id)
        form = self.schema().load(request.get_json())
        try:
            groups = [self.group_dao.get_by(id=group['id']) for group in form['groups']]
        except NotFoundError as e:
            raise errors.param_not_found('groups', 'Group', **e.metadata)

        self.service.associate_all_groups(user, groups)

        return '', 204
