# -*- coding: utf-8 -*-
# Copyright 2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.call_permission import dao as call_permission_dao
from xivo_dao.resources.group import dao as group_dao

from .resource import GroupCallPermissionAssociation
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            GroupCallPermissionAssociation,
            '/groups/<int:group_id>/callpermissions/<int:call_permission_id>',
            endpoint='group_call_permissions',
            resource_class_args=(service, group_dao, call_permission_dao)
        )
