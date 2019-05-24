# Copyright 2017-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.paging import dao as paging_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import PagingCallerUserItem, PagingMemberUserItem
from .service import build_service


class Plugin:

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            PagingCallerUserItem,
            '/pagings/<int:paging_id>/callers/users',
            endpoint='paging_caller_users',
            resource_class_args=(service, paging_dao, user_dao)
        )

        api.add_resource(
            PagingMemberUserItem,
            '/pagings/<int:paging_id>/members/users',
            endpoint='paging_member_users',
            resource_class_args=(service, paging_dao, user_dao)
        )
