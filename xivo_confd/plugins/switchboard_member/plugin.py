# -*- coding: utf-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.switchboard import dao as switchboard_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import SwitchboardMemberUserItem
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            SwitchboardMemberUserItem,
            '/switchboards/<uuid:switchboard_uuid>/members/users',
            endpoint='switchboard_member_users',
            resource_class_args=(service, switchboard_dao, user_dao)
        )
