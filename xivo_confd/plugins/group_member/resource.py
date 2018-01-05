# -*- coding: UTF-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request
from marshmallow import fields, post_load

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.mallow import BaseSchema
from xivo_confd.helpers.restful import ConfdResource


class GroupUserSchema(BaseSchema):
    uuid = fields.String(required=True)
    priority = fields.Integer()

    @post_load
    def add_envelope(self, data):
        data['user'] = {'uuid': data.pop('uuid')}
        return data


class GroupUsersSchema(BaseSchema):
    users = fields.Nested(GroupUserSchema, many=True, required=True)

    @post_load
    def set_default_priority(self, data):
        for priority, user in enumerate(data['users']):
            user['priority'] = user.get('priority', priority)
        return data


class GroupExtensionSchema(BaseSchema):
    exten = fields.String(required=True)
    context = fields.String(required=True)
    priority = fields.Integer()

    @post_load
    def add_envelope(self, data):
        data['extension'] = {'exten': data.pop('exten'),
                             'context': data.pop('context')}
        return data


class GroupExtensionsSchema(BaseSchema):
    extensions = fields.Nested(GroupExtensionSchema, many=True, required=True)

    @post_load
    def set_default_priority(self, data):
        for priority, extension in enumerate(data['extensions']):
            extension['priority'] = extension.get('priority', priority)
        return data


class GroupMemberItem(ConfdResource):
    def __init__(self, service, group_dao):
        super(GroupMemberItem, self).__init__()
        self.service = service
        self.group_dao = group_dao


class GroupMemberUserItem(GroupMemberItem):

    schema = GroupUsersSchema

    def __init__(self, service, group_dao, user_dao):
        super(GroupMemberUserItem, self).__init__(service, group_dao)
        self.user_dao = user_dao

    @required_acl('confd.groups.{group_id}.members.users.update')
    def put(self, group_id):
        group = self.group_dao.get(group_id)
        form = self.schema().load(request.get_json()).data
        try:
            for user in form['users']:
                user['user'] = self.user_dao.get_by(uuid=user['user']['uuid'])
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_users(group, form['users'])
        return '', 204


class GroupMemberExtensionItem(GroupMemberItem):

    schema = GroupExtensionsSchema

    @required_acl('confd.groups.{group_id}.members.extensions.update')
    def put(self, group_id):
        group = self.group_dao.get(group_id)
        form = self.schema().load(request.get_json()).data
        self.service.associate_all_extensions(group, form['extensions'])
        return '', 204
