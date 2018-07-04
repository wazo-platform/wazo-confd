# -*- coding: utf-8 -*-
# Copyright 2016-2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from flask import request

from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import GroupUsersSchema, GroupExtensionsSchema


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
