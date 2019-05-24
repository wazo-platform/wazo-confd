# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from flask import request

from xivo_dao.alchemy.queuemember import QueueMember
from xivo_dao.helpers import errors
from xivo_dao.helpers.exception import NotFoundError

from xivo_confd.auth import required_acl
from xivo_confd.helpers.restful import ConfdResource

from .schema import GroupUsersSchema, GroupExtensionsSchema


class Extension:

    def __init__(self, exten=None, context=None):
        self.exten = exten
        self.context = context


class GroupMemberItem(ConfdResource):
    def __init__(self, service, group_dao):
        super(GroupMemberItem, self).__init__()
        self.service = service
        self.group_dao = group_dao


class GroupMemberUserItem(GroupMemberItem):

    schema = GroupUsersSchema
    has_tenant_uuid = True

    def __init__(self, service, group_dao, user_dao):
        super(GroupMemberUserItem, self).__init__(service, group_dao)
        self.user_dao = user_dao

    @required_acl('confd.groups.{group_id}.members.users.update')
    def put(self, group_id):
        tenant_uuids = self._build_tenant_list({'recurse': True})

        group = self.group_dao.get(group_id, tenant_uuids=tenant_uuids)
        form = self.schema().load(request.get_json()).data
        members = []
        try:
            for member_form in form['users']:
                user = self.user_dao.get_by(uuid=member_form['user']['uuid'], tenant_uuids=tenant_uuids)
                member = self._find_or_create_member(group, user)
                member.priority = member_form['priority']
                members.append(member)
        except NotFoundError as e:
            raise errors.param_not_found('users', 'User', **e.metadata)

        self.service.associate_all_users(group, members)
        return '', 204

    def _find_or_create_member(self, group, user):
        member = self.service.find_member_user(group, user)
        if not member:
            member = QueueMember(user=user)
        return member


class GroupMemberExtensionItem(GroupMemberItem):

    schema = GroupExtensionsSchema

    @required_acl('confd.groups.{group_id}.members.extensions.update')
    def put(self, group_id):
        group = self.group_dao.get(group_id)
        form = self.schema().load(request.get_json()).data
        members = []
        for member_form in form['extensions']:
            extension = Extension(**member_form['extension'])
            member = self._find_or_create_member(group, extension)
            member.priority = member_form['priority']
            members.append(member)

        self.service.associate_all_extensions(group, members)
        return '', 204

    def _find_or_create_member(self, group, extension):
        member = self.service.find_member_extension(group, extension)
        if not member:
            member = QueueMember(extension=extension)
        return member
