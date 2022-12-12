# Copyright 2016-2019 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

from xivo_dao.resources.user import dao as user_dao

from .middleware import UserFallbackMiddleWare
from .resource import UserFallbackList
from .service import build_service


class Plugin:
    def load(self, dependencies):
        api = dependencies['api']
        middleware_handle = dependencies['middleware_handle']
        user_fallback_service = build_service()

        user_fallback_association_middleware = UserFallbackMiddleWare(user_fallback_service)
        middleware_handle.register(
            'user_fallback_association', user_fallback_association_middleware
        )


        api.add_resource(
            UserFallbackList,
            '/users/<uuid:user_id>/fallbacks',
            '/users/<int:user_id>/fallbacks',
            resource_class_args=(user_fallback_service, user_dao,user_fallback_association_middleware,),
        )
