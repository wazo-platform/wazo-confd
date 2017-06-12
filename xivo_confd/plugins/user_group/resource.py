# -*- coding: UTF-8 -*-

# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>

from flask import request
from marshmallow import fields

from xivo_confd.authentication.confd_auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError


class GroupSchemaIDLoad(BaseSchema):
    id = fields.Integer(required=True)


class GroupsIDSchema(BaseSchema):
    groups = fields.Nested(GroupSchemaIDLoad, many=True, required=True)


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
        form = self.schema().load(request.get_json()).data
        try:
            groups = [self.group_dao.get_by(id=group['id']) for group in form['groups']]
        except NotFoundError as e:
            raise errors.param_not_found('groups', 'Group', **e.metadata)

        self.service.associate_all_groups(user, groups)

        return '', 204
