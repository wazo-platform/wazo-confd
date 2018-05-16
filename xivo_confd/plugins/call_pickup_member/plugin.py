# -*- coding: utf-8 -*-
# Copyright 2018 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0+

from xivo_dao.resources.call_pickup import dao as call_pickup_dao
from xivo_dao.resources.user import dao as user_dao

from .resource import CallPickupInterceptorUserList, CallPickupTargetUserList
from .service import build_service


class Plugin(object):

    def load(self, dependencies):
        api = dependencies['api']
        service = build_service()

        api.add_resource(
            CallPickupInterceptorUserList,
            '/callpickups/<int:call_pickup_id>/interceptors/users',
            endpoint='call_pickup_interceptors_users',
            resource_class_args=(service, call_pickup_dao, user_dao)
        )

        api.add_resource(
            CallPickupTargetUserList,
            '/callpickups/<int:call_pickup_id>/targets/users',
            endpoint='call_pickup_target_users',
            resource_class_args=(service, call_pickup_dao, user_dao)
        )
