# Copyright 2018-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.call_pickup import dao as call_pickup_dao
from xivo_dao.resources.group import dao as group_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import (
    CallPickupInterceptorGroupList,
    CallPickupInterceptorUserList,
    CallPickupTargetGroupList,
    CallPickupTargetUserList,
)
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CallPickupInterceptorGroupList,
            '/callpickups/<int:call_pickup_id>/interceptors/groups',
            endpoint='call_pickup_interceptors_groups',
            resource_class_args=(service, call_pickup_dao, group_dao),
        )

        api.add_resource(
            CallPickupTargetGroupList,
            '/callpickups/<int:call_pickup_id>/targets/groups',
            endpoint='call_pickup_target_groups',
            resource_class_args=(service, call_pickup_dao, group_dao),
        )

        api.add_resource(
            CallPickupInterceptorUserList,
            '/callpickups/<int:call_pickup_id>/interceptors/users',
            endpoint='call_pickup_interceptors_users',
            resource_class_args=(service, call_pickup_dao, user_dao),
        )

        api.add_resource(
            CallPickupTargetUserList,
            '/callpickups/<int:call_pickup_id>/targets/users',
            endpoint='call_pickup_target_users',
            resource_class_args=(service, call_pickup_dao, user_dao),
        )
