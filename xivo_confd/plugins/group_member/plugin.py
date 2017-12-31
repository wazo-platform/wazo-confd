# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import GroupMemberUserItem, GroupMemberExtensionItem
from .service import build_service


class Plugin(object):

    def load(self, core):
        api = core['api']
        service = build_service()

        api.add_resource(
            GroupMemberUserItem,
            '/groups/<int:group_id>/members/users',
            endpoint='group_member_users',
            resource_class_args=(service, group_dao, user_dao)
        )

        api.add_resource(
            GroupMemberExtensionItem,
            '/groups/<int:group_id>/members/extensions',
            endpoint='group_member_extensions',
            resource_class_args=(service, group_dao)
        )
