# -*- coding: UTF-8 -*-
# Copyright 2016-2017 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.user import dao as user_dao
from xivo_dao.resources.call_permission import dao as call_permission_dao

from xivo_confd import api

from .resource import (
    CallPermissionUserGet,
    UserCallPermissionAssociation,
    UserCallPermissionGet,
)
from .service import build_service


class Plugin(object):

    def load(self, core):
        service = build_service()

        api.add_resource(
            UserCallPermissionAssociation,
            '/users/<uuid:user_id>/callpermissions/<int:call_permission_id>',
            '/users/<int:user_id>/callpermissions/<int:call_permission_id>',
            endpoint='user_call_permissions',
            resource_class_args=(service, user_dao, call_permission_dao)
        )

        api.add_resource(
            UserCallPermissionGet,
            '/users/<uuid:user_id>/callpermissions',
            '/users/<int:user_id>/callpermissions',
            resource_class_args=(service, user_dao, call_permission_dao)
        )

        api.add_resource(
            CallPermissionUserGet,
            '/callpermissions/<int:call_permission_id>/users',
            resource_class_args=(service, user_dao, call_permission_dao)
        )
