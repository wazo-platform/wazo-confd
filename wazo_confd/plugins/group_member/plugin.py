# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import GroupMemberExtensionItem, GroupMemberUserItem
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            GroupMemberUserItem,
            '/groups/<int:group_uuid>/members/users',
            '/groups/<uuid:group_uuid>/members/users',
            endpoint='group_member_users',
            resource_class_args=(service, group_dao, user_dao),
        )

        api.add_resource(
            GroupMemberExtensionItem,
            '/groups/<int:group_uuid>/members/extensions',
            '/groups/<uuid:group_uuid>/members/extensions',
            endpoint='group_member_extensions',
            resource_class_args=(service, group_dao),
        )
