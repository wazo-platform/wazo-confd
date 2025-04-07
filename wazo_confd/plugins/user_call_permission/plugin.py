# Copyright 2016-2025 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.call_permission import dao as call_permission_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import UserCallPermissionAssociation
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            UserCallPermissionAssociation,
            '/users/<uuid:user_id>/callpermissions/<int:call_permission_id>',
            '/users/<int:user_id>/callpermissions/<int:call_permission_id>',
            endpoint='user_call_permissions',
            resource_class_args=(service, user_dao, call_permission_dao),
        )
